import requests
from bs4 import BeautifulSoup

async def analyze_url_content(url):
    result = False
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    clean_text = '\n'.join(line for line in lines if line)

    if not clean_text:
        print("Could not find any text on the page.")
        return

    word_count = len(clean_text.split())
    if word_count > 250:
        result = True
    return result

