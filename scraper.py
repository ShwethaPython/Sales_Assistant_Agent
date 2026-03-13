import requests
from bs4 import BeautifulSoup
import re

# ── The ONLY URLs scraped automatically ──────────────────────────────────────
# Just Nike's own pages — no competitor scraping needed.
# The LLM already knows Nike's competitors from its training data.
NIKE_PAGES = [
    "https://www.nike.com",
    "https://about.nike.com/en",
    "https://investors.nike.com/investors/news-events-and-reports/press-releases/press-release-details/2024/NIKE-Inc.-Reports-Fiscal-2024-Fourth-Quarter-and-Full-Year-Results/default.aspx",
]

# Competitor names passed as text to the LLM — no scraping required
NIKE_COMPETITORS = ["Adidas", "Under Armour", "Puma", "New Balance", "Lululemon"]


def scrape_url(url: str, max_chars: int = 3000) -> str:
    """
    Visit one URL and return up to max_chars of clean plain text.

    What it does step by step:
      1. Sends an HTTP GET request to the URL
      2. Parses the HTML with BeautifulSoup
      3. Removes all noise tags (scripts, styles, nav, footer, etc.)
      4. Extracts plain text
      5. Collapses whitespace
      6. Returns the first max_chars characters

    Expected output — a plain text string, e.g.:
      "Nike React Infinity Run Flyknit. Free Shipping & Returns.
       Nike Members get free shipping. Just Do It. Find your
       favourite shoes, clothing and accessories..."
    """
    if not url:
        return ""
    if not url.startswith("http"):
        url = "https://" + url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Strip noise — we only want readable content
        for tag in soup(["script", "style", "nav", "footer",
                          "header", "aside", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)   # collapse whitespace
        return text[:max_chars]

    except Exception as e:
        # Return an error string — the LLM handles missing data gracefully
        return f"[Could not retrieve {url}: {e}]"


def scrape_nike_pages() -> dict[str, str]:
    """
    Scrape Nike's homepage, About page, and latest earnings press release.

    Returns a dict like:
    {
        "https://www.nike.com":        "Nike React Infinity Run...",
        "https://about.nike.com/en":   "Our Mission: Bring inspiration...",
        "https://investors.nike.com/...": "NIKE Q4 FY2024 revenues $51.4B..."
    }

    This is the ONLY scraping that happens automatically.
    Competitors are NOT scraped — the LLM uses its own knowledge instead.
    """
    results = {}
    for url in NIKE_PAGES:
        results[url] = scrape_url(url, max_chars=2500)
    return results
