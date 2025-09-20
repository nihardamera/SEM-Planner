from typing import List, Dict
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client (using the provided API key)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY", os.getenv("GROK_API_KEY", "your_groq_api_key_here")),
    base_url="https://api.groq.com/openai/v1",
)

async def generate_seed_keywords(url: str) -> List[str]:
    """Generate seed keywords using Groq API."""
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
            temperature=0.7
        )

        keywords_text = response.choices[0].message.content
        keywords = keywords_text.split(',') if ',' in keywords_text else keywords_text.split('\n')
        return [kw.strip() for kw in keywords if kw.strip()]

    except Exception as e:
        print(f"Groq API error in generate_seed_keywords: {e}")
        # Fallback to static keywords based on URL
        brand_name = url.replace('https://', '').replace('http://', '').replace('www.', '').split('.')[0]
        return [
            f"{brand_name}",
            f"{brand_name} shoes",
            "comfortable sneakers",
            "sustainable footwear",
            "eco friendly shoes",
            "walking shoes",
            "casual sneakers",
            "athletic footwear",
            "running shoes",
            "workout sneakers",
            "all day comfort",
            "breathable shoes",
            "lightweight sneakers",
            "everyday shoes",
            "premium footwear"
        ]

async def cluster_keywords(keywords: List[str]) -> Dict[str, List[str]]:
    """Cluster keywords into ad groups using Groq API."""
    prompt = f"""Act as a senior Google Ads specialist organizing a new search campaign given a list of high-potential keywords for a brand.
Group the keywords into 4-6 distinct, tightly themed ad groups using logical segmentation. Each group should have a concise name and a list of related keywords.

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
            max_tokens=800,
            temperature=0.3
        )

        response_text = response.choices[0].message.content.strip()
        # Clean up the response to extract JSON
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].strip()

        ad_groups = json.loads(response_text)
        return ad_groups

    except Exception as e:
        print(f"Groq API error in cluster_keywords: {e}")
        # Fallback to simple clustering
        return create_fallback_clusters(keywords)

async def generate_pmax_themes(ad_group_themes: List[str]) -> List[str]:
    """Generate PMax themes using Groq API."""
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
            temperature=0.6
        )

        themes_text = response.choices[0].message.content
        themes = themes_text.split('\n') if '\n' in themes_text else themes_text.split(',')
        clean_themes = []
        for theme in themes:
            theme = theme.strip()
            # Remove numbering and bullet points
            theme = theme.replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').replace('6.', '')
            theme = theme.replace('-', '').replace('•', '').strip()
            if theme and len(theme) <= 80:
                clean_themes.append(theme)

        return clean_themes[:6] if clean_themes else create_fallback_pmax_themes()

    except Exception as e:
        print(f"Groq API error in generate_pmax_themes: {e}")
        return create_fallback_pmax_themes()


def create_fallback_clusters(keywords: List[str]) -> Dict[str, List[str]]:
    """Create fallback keyword clusters when API fails."""
    brand_keywords = [kw for kw in keywords if any(brand in kw.lower() for brand in ['allbirds', 'nike', 'adidas'])]
    comfort_keywords = [kw for kw in keywords if any(word in kw.lower() for word in ['comfort', 'soft', 'cushion', 'support'])]
    sustainable_keywords = [kw for kw in keywords if any(word in kw.lower() for word in ['sustainable', 'eco', 'green', 'organic'])]
    athletic_keywords = [kw for kw in keywords if any(word in kw.lower() for word in ['athletic', 'running', 'workout', 'sport', 'gym'])]

    # Remaining keywords
    used_keywords = set(brand_keywords + comfort_keywords + sustainable_keywords + athletic_keywords)
    general_keywords = [kw for kw in keywords if kw not in used_keywords]

    clusters = {}
    if brand_keywords:
        clusters["Brand Terms"] = brand_keywords
    if comfort_keywords:
        clusters["Comfort & Support"] = comfort_keywords
    if sustainable_keywords:
        clusters["Sustainable Footwear"] = sustainable_keywords
    if athletic_keywords:
        clusters["Athletic & Performance"] = athletic_keywords
    if general_keywords:
        clusters["General Footwear"] = general_keywords

    return clusters


def create_fallback_pmax_themes() -> List[str]:
    """Create fallback PMax themes when API fails."""
    return [
        "Premium Comfort Footwear",
        "Sustainable & Eco-Friendly Shoes",
        "Athletic Performance Sneakers",
        "Everyday Casual Comfort",
        "Professional & Lifestyle",
        "Active Outdoor Adventures"
    ]
