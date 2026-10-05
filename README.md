# SEM Planner

Given a brand's website, a competitor's website, an average product price and a target return on ad spend (ROAS), SEM Planner drafts a Google Ads plan with three parts:

- **Search campaigns**: ad groups of keywords, each keyword with its search volume, competition and top-of-page bid range, plus a suggested CPC range per ad group.
- **Performance Max themes**: up to six search themes for a Performance Max asset group.
- **Shopping bids**: a target CPA and a target CPC derived from the price and the ROAS target.

The backend is a FastAPI app (Python). The frontend is a React app built with Vite.

## How the work is split

Each part of the plan comes from the tool that is suited to it. The language model never sets a number.

| Part of the plan | Comes from |
| --- | --- |
| Search volumes, competition, top-of-page bids | Google Keyword Planner (Google Ads API, `KeywordPlanIdeaService`) |
| Which keywords are kept, and their order | A fixed weighted score (below) |
| Ad group names, and which keywords go in which group | Language model (Groq) |
| CPC range of each ad group | Mean of its keywords' Keyword Planner bids |
| Performance Max themes | Language model |
| Shopping target CPA and CPC | A formula (below) |
| Seed keywords, when needed | Keyword Planner ideas for the brand URL, or the language model (see step 2) |

### Pipeline

1. Fetch the brand page and extract its visible text (requests and BeautifulSoup; JavaScript is not run).
2. Pick up to 20 seed keywords. If the page has more than 250 words and Keyword Planner is available, the seeds are the first 20 Keyword Planner ideas for the brand URL. Otherwise the language model suggests up to 15 seeds from the page text (first 3,000 characters), or from the URL alone if the page could not be fetched.
3. Ask Keyword Planner for keyword ideas with metrics, sending the seeds and the competitor URL together in one `keyword_and_url_seed`. The API accepts at most 20 seeds, so the backend never sends more.
4. Rank the ideas with the weighted score and keep the top 50.
5. Ask the language model to sort the ranked keywords into 5 to 7 named ad groups. Keywords the model invents or rewrites are dropped. Ranked keywords it leaves out are shown in an "Ungrouped keywords" group.
6. Set each ad group's CPC range to the mean low top-of-page bid and the mean high top-of-page bid of its keywords.
7. Ask the language model for Performance Max themes (at most 80 characters each) based on the ad group names and their top keywords.
8. Calculate the Shopping bids with the formula.

The suggested match types (Phrase and Exact) are the same fixed suggestion for every ad group.

### Ranking score

Keywords with fewer than 500 average monthly searches are dropped. Each remaining keyword gets:

```
score = 0.4 * V + 0.4 * B - 0.2 * C
```

- `V` is the average monthly searches.
- `B` is the average top-of-page bid, `(low bid + high bid) / 2`. A higher bid is read as a sign of commercial intent.
- `C` is Keyword Planner's competition index (0 to 100).

Each of `V`, `B` and `C` is min-max normalised to 0 to 1 across the keywords that passed the volume filter: `(x - min) / (max - min)`, or 0 when all values are equal. The 50 highest scores are kept. The weights are fixed choices, not fitted to data. They are constants in `backend/sem_plan.py`, and the interface prints the formula above the ad groups.

### Shopping bid formula

```
target CPA = average product price / (target ROAS / 100)
target CPC = target CPA * ASSUMED_CONVERSION_RATE
```

`ASSUMED_CONVERSION_RATE` is 0.02 (2% of clicks lead to a sale). It is an assumption, not a figure from any account. It is defined in `backend/sem_plan.py`, returned in the API response and shown in the interface. Example: a $110 product with a 400% ROAS target gives a target CPA of 110 / 4 = $27.50 and a target CPC of 27.50 * 0.02 = $0.55.

## Estimated-data mode

Keyword Planner data needs a Google Ads developer token, and Google has to approve a token's access level before it works with real accounts. A token that is only approved for test accounts is rejected with `DEVELOPER_TOKEN_NOT_APPROVED`. The estimated-data mode lets the whole pipeline run before that approval.

The backend switches to this mode when `backend/google-ads.yaml` is missing, `GOOGLE_ADS_CUSTOMER_ID` is not set, the configuration cannot be loaded, or a Keyword Planner request fails for any reason. In this mode:

- The API response has `"data_source": "estimated"` and an `estimated_reason`, for example `The Google Ads developer token is not approved for production accounts yet (DEVELOPER_TOKEN_NOT_APPROVED).` With real data it has `"data_source": "keyword_planner"`.
- The interface shows an orange banner with the reason, and the Search section is labelled "Estimated figures".
- Volumes, competition and bids are placeholders, not market data. Each keyword gets values in a range chosen by its word count, drawn from a random generator seeded with a SHA-256 hash of the keyword text. The same keyword always gets the same values.
- The keyword list is the seed keywords plus generic brand terms built from the brand's domain name (`acme`, `acme store`, `acme online`, `buy acme`, `acme reviews`) and two competitor terms (`rival`, `rival alternative`).

| Keyword type | Monthly searches | Competition | Low bid | High bid |
| --- | --- | --- | --- | --- |
| 1 word | 5,000 to 50,000 | 60 to 90 | $1.00 to $3.00 | $3.00 to $8.00 |
| 2 words | 1,000 to 15,000 | 40 to 70 | $0.80 to $2.50 | $2.50 to $6.00 |
| 3 or more words | 100 to 5,000 | 20 to 50 | $0.50 to $2.00 | $2.00 to $4.00 |
| Brand and competitor terms | 500 to 8,000 | 80 to 100 | $0.30 to $1.50 | $1.50 to $3.50 |

Do not use estimated figures to set real budgets or bids. The ranking, grouping and themes are still produced the same way, so the mode is useful for trying the tool, not for planning spend.

## Setup

Requirements: Python 3.12 (the pinned versions were installed and tested with 3.12), [uv](https://docs.astral.sh/uv/), and Node.js 20.19+ or 22.12+ for the frontend (required by Vite 7).

```
git clone https://github.com/nihardamera/SEM-Planner.git
cd SEM-Planner
```

### Backend

```
uv venv --python 3.12 .venv
uv pip install -r requirements-dev.txt    # requirements.txt alone if you do not need the tests
cp backend/.env.example backend/.env
```

Set `GROQ_API_KEY` in `backend/.env`. You can create a key at https://console.groq.com/keys. Without it, plan requests return HTTP 502 with a message saying the key is not set.

Keyword Planner (optional; without it the backend uses estimated data):

```
cp backend/google-ads.yaml.example backend/google-ads.yaml
```

Fill in the developer token, OAuth client ID and secret, refresh token and, if you reach the account through a manager account, `login_customer_id`. Then set `GOOGLE_ADS_CUSTOMER_ID` in `backend/.env` to the account the Keyword Planner requests run under. Both `backend/.env` and `backend/google-ads.yaml` are in `.gitignore`; do not commit them.

Run the backend:

```
cd backend
../.venv/bin/uvicorn main:app --reload --port 8000
```

`GET http://localhost:8000/api/v1/health` reports whether the Groq key and the Google Ads configuration are present. The interactive API docs are at http://localhost:8000/docs.

### Frontend

```
cd frontend
npm ci
npm run dev
```

The dev server runs at http://localhost:5173 and calls the backend at http://localhost:8000. To use another backend, set `VITE_API_URL` to its base URL (without `/api/v1`) when you run or build the frontend, for example in `frontend/.env.local` (see `frontend/.env.example`):

```
VITE_API_URL=https://your-backend.example.com npm run build
```

The backend only accepts browser requests from the origins in `CORS_ORIGINS`, so add the frontend's origin there.

### Tests

```
.venv/bin/python -m pytest backend/tests
```

The tests replace Groq and the Google Ads API with fakes, so they need no keys and make no network calls. They cover the Keyword Planner path, the 20-seed cap, the switch to estimated data, error responses, the ranking score and the Shopping formula.

## Configuration

| Setting | Where | Default | Purpose |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | `backend/.env` | none (required) | Groq API key for the language model calls |
| `GROQ_MODEL` | `backend/.env` | `llama-3.1-8b-instant` | Groq model name |
| `GOOGLE_ADS_CUSTOMER_ID` | `backend/.env` | none | Google Ads account for Keyword Planner requests |
| `GOOGLE_ADS_CONFIGURATION_FILE_PATH` | `backend/.env` | `backend/google-ads.yaml` | Google Ads client configuration |
| `CORS_ORIGINS` | `backend/.env` | `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:4173` | Comma-separated origins allowed to call the API |
| `VITE_API_URL` | frontend build environment | `http://localhost:8000` | Backend base URL |

## API

`POST /api/v1/plan`

```json
{
  "brand_url": "https://www.example.com",
  "competitor_url": "https://www.example.org",
  "average_product_price": 110,
  "target_roas_percentage": 400
}
```

The response contains `data_source`, `estimated_reason`, `seed_keywords`, `seed_source`, `search_campaign_plan` (ad groups with per-keyword metrics and scores, plus the ranking settings), `pmax_plan` and `shopping_campaign_plan` (including `assumed_conversion_rate`). The full schema is at `/docs`.

Errors: 422 for invalid input (for example a URL without `http://` or `https://`), 502 with a plain message when a language model call fails, and 500 with a generic message for anything else. Error responses do not include raw exception text; details go to the backend log.

`GET /api/v1/health` returns the status and whether Groq and Google Ads are configured.

## Limitations

- Keyword Planner requests set no location or language targeting, so volumes and bids are not limited to a market.
- Keyword Planner returns bids in the Google Ads account's currency. The interface prints a `$` sign, which is only correct for a USD account.
- The page text comes from the raw HTML. Sites that render their content with JavaScript look thin, so their seeds come from the language model instead of a Keyword Planner URL seed.
- Language model output can differ between runs, even at temperature 0, so the grouping and themes may change for the same input. Only the estimated figures are fixed per keyword.
- The 250-word threshold, the 500-search filter, the ranking weights and the 2% conversion rate are fixed choices, not values learned from data.
- The backend fetches whatever URL it is given and has no authentication or rate limiting. Do not expose it publicly as is.
- `Procfile` and `railway.json` start the backend with uvicorn on hosts that read them. They were not tested as part of this cleanup.

## Project layout

```
backend/
  main.py              FastAPI app, CORS, .env loading
  api_endpoints.py     /api/v1/plan and /api/v1/health
  sem_plan.py          pipeline, ranking score, CPC ranges, Shopping formula
  keyword_planner.py   Google Ads Keyword Planner requests
  estimates.py         estimated-data mode
  llm_calls.py         Groq prompts and response parsing
  url_checker.py       page fetch and text extraction
  models.py            request and response models
  tests/               pytest suite with fakes for Groq and Google Ads
frontend/
  src/                 React components and the API client (PlanApi.js)
```
