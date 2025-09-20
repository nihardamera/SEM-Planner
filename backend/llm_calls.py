from typing import List, Dict
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY", os.getenv("GROK_API_KEY", "your_groq_api_key_here")),
)

async def generate_seed_keywords(url: str) -> List[str]:
    prompt = f"""Act as an expert SEM strategist with 15 years of experience in e-commerce.
                 Analyze the content of the website given. Based on the specific products and services offered, generate a list of 15 seed keywords that capture the core offerings.
                 Prioritize keywords that a potential customer ready to make a purchase would use. Return the keywords as a comma-separated list.
                 URL: {url}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert SEM strategist with 15 years of experience in e-commerce."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )

        keywords_text = response.choices[0].message.content
        keywords = keywords_text.split(',') if ',' in keywords_text else keywords_text.split('\n')
        return [kw.strip() for kw in keywords if kw.strip()]

    except Exception as e:
        print(f"Groq API error in generate_seed_keywords: {e}")
        return
    
async def cluster_keywords(keywords: List[str]) -> Dict[str, List[str]]:
    prompt = f"""Act as a senior Google Ads specialist organizing a new search campaign given a list of high-potential keywords for a brand.
Group the keywords into 5-7 distinct, tightly themed ad groups using logical segmentation. Each group should have a concise name and a list of related keywords.
The segmentation strategy should follow established best practices, creating distinct ad groups for different types of user intent:
- Brand Terms: Ad groups dedicated to keywords that include the brand's own name . These typically have the highest conversion rates and should be isolated to track their performance accurately.
- Category/Generic Terms: These ad groups target broader product or service categories. They are crucial for attracting new customers who are not yet familiar with the brand.
- Competitor Terms: A more aggressive strategy involves creating ad groups that bid on competitors' brand names. This can be effective for capturing market share from users who are close to making a purchase decision.
- Location-Based Queries: For businesses with a physical presence or geographically-specific services, targeting location-based queries can be effective.
- Long-Tail/Informational Queries: These ad groups target longer, more specific, often question-based keywords. While lower in volume, they capture users in the research phase and can be targeted with content-driven landing pages.
Guidelines:
- Return ONLY a valid JSON object where keys are ad group names and values are lists of keywords
- Do not include any explanatory text, just the JSON
- Group similar keywords together logically
- Use descriptive ad group names

Keywords to group: {keywords}

Example format:
{{"Brand Terms": ["keyword1", "keyword2"], "Product Category": ["keyword3", "keyword4"]}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a senior Google Ads specialist. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )

        response_text = response.choices[0].message.content.strip()
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].strip()

        ad_groups = json.loads(response_text)
        return ad_groups

    except Exception as e:
        print(f"Groq API error in cluster_keywords: {e}")
        return

async def generate_pmax_themes(ad_group_themes: List[str]) -> List[str]:
    prompt = f"""Act as a Google Ads AI strategist.
Generate 6 concise Search Themes for a Performance Max campaign based on these ad group themes.
Each theme should be a short phrase, up to 80 characters, covering:
- Product categories
- Use cases
- Target demographics
- Seasonal opportunities

Return themes as a simple list, one per line.

Ad group themes: {ad_group_themes}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a Google Ads AI strategist. Generate concise PMax themes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.4
        )

        themes_text = response.choices[0].message.content
        themes = themes_text.split('\n') if '\n' in themes_text else themes_text.split(',')
        clean_themes = []
        for theme in themes:
            theme = theme.strip()
            theme = theme.replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').replace('6.', '')
            theme = theme.replace('-', '').replace('•', '').strip()
            if theme and len(theme) <= 80:
                clean_themes.append(theme)

        return clean_themes[:6]

    except Exception as e:
        print(f"Groq API error in generate_pmax_themes: {e}")
        return 

