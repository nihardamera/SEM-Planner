"""Test fixtures. No test touches the network, a real API key or a real config file.

Groq is replaced by FakeGroq. The Google Ads client is replaced by
FakeAdsClient, which builds real request and result messages with the
google-ads library but answers generate_keyword_ideas itself.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import keyword_planner  # noqa: E402
import llm_calls  # noqa: E402
import sem_plan  # noqa: E402

BRAND_URL = "https://www.example-brand.com"
COMPETITOR_URL = "https://www.example-rival.com"

RICH_PAGE_TEXT = " ".join(["Lightweight running shoes and waterproof hiking boots."] * 60)
THIN_PAGE_TEXT = "Handmade running shoes. Free shipping."


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch, tmp_path):
    for name in ("GROQ_API_KEY", "GROQ_MODEL", "GOOGLE_ADS_CUSTOMER_ID", "CORS_ORIGINS"):
        monkeypatch.delenv(name, raising=False)
    # Point at a file that does not exist, so a real google-ads.yaml is never read.
    monkeypatch.setenv("GOOGLE_ADS_CONFIGURATION_FILE_PATH", str(tmp_path / "absent-google-ads.yaml"))
    monkeypatch.setattr(sem_plan, "fetch_page_text", lambda url: THIN_PAGE_TEXT)


class FakeGroq:
    """Stands in for groq.Groq. Picks a reply by the kind of prompt it receives."""

    def __init__(self, seeds="", groups=None, themes="", error=None):
        self.seeds = seeds
        self.groups = groups or {}
        self.themes = themes
        self.error = error
        self.prompts = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model, messages, max_tokens, temperature):
        prompt = messages[-1]["content"]
        self.prompts.append(prompt)
        if self.error is not None:
            raise self.error
        if "seed keywords" in prompt:
            text = self.seeds
        elif "Group these Google Ads keywords" in prompt:
            text = self.groups if isinstance(self.groups, str) else "```json\n" + json.dumps(self.groups) + "\n```"
        elif "Performance Max" in prompt:
            text = self.themes
        else:
            raise AssertionError(f"Unexpected prompt: {prompt[:80]}")
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])

    def prompts_containing(self, marker):
        return [prompt for prompt in self.prompts if marker in prompt]


@pytest.fixture
def fake_groq(monkeypatch):
    def install(**kwargs):
        fake = FakeGroq(**kwargs)
        monkeypatch.setenv("GROQ_API_KEY", "not-a-real-key")
        monkeypatch.setattr(llm_calls, "_get_client", lambda: fake)
        return fake

    return install


def _library_client():
    from google.ads.googleads.client import GoogleAdsClient
    from google.auth.credentials import AnonymousCredentials

    return GoogleAdsClient(credentials=AnonymousCredentials(), developer_token="placeholder", use_proto_plus=True)


class FakeIdeaService:
    def __init__(self, responder):
        self.responder = responder
        self.requests = []

    def generate_keyword_ideas(self, request):
        self.requests.append(request)
        return self.responder(request)


class FakeAdsClient:
    def __init__(self, responder):
        self._library = _library_client()
        self.service = FakeIdeaService(responder)

    def get_type(self, name):
        return self._library.get_type(name)

    def get_service(self, name):
        assert name == "KeywordPlanIdeaService"
        return self.service


def make_idea(text, searches=0, competition=0, low=0.0, high=0.0):
    idea = _library_client().get_type("GenerateKeywordIdeaResult")
    idea.text = text
    metrics = idea.keyword_idea_metrics
    metrics.avg_monthly_searches = searches
    metrics.competition_index = competition
    metrics.low_top_of_page_bid_micros = round(low * 1_000_000)
    metrics.high_top_of_page_bid_micros = round(high * 1_000_000)
    return idea


def developer_token_not_approved():
    from google.ads.googleads.errors import GoogleAdsException

    client = _library_client()
    failure = client.get_type("GoogleAdsFailure")
    error = client.get_type("GoogleAdsError")
    error.error_code.authorization_error = client.get_type(
        "AuthorizationErrorEnum"
    ).AuthorizationError.DEVELOPER_TOKEN_NOT_APPROVED
    error.message = "The developer token is only approved for use with test accounts."
    failure.errors.append(error)
    return GoogleAdsException(None, None, failure, "test-request-id")


@pytest.fixture
def fake_ads(monkeypatch, tmp_path):
    """Make Keyword Planner look configured and answer with `responder(request)`."""

    def install(responder):
        config = tmp_path / "google-ads.yaml"
        config.write_text("# placeholder, never loaded: _load_client is replaced\n")
        monkeypatch.setenv("GOOGLE_ADS_CONFIGURATION_FILE_PATH", str(config))
        monkeypatch.setenv("GOOGLE_ADS_CUSTOMER_ID", "000-000-0000")
        client = FakeAdsClient(responder)
        monkeypatch.setattr(keyword_planner, "_load_client", lambda: client)
        return client.service

    return install
