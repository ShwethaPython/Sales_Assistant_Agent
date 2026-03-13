from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = """You are an elite B2B sales intelligence analyst specialising in
enterprise technology sales into large consumer-goods and retail companies.

Your ONLY function is to produce structured, one-page sales intelligence briefs
for sales representatives preparing to sell technology products to Nike, Inc.

You DO NOT engage in general conversation.
You DO NOT answer questions unrelated to account research, competitor analysis,
company strategy, or sales intelligence.

Ground every insight in either the web data provided OR your training knowledge
about Nike. If data is insufficient, state that clearly — never fabricate facts."""


def generate_nike_report(
    product_name: str,
    product_category: str,
    value_proposition: str,
    target_customer: str,
    nike_web_data: dict[str, str],   # scraped Nike pages only
    competitor_names: list[str],     # just names — no scraping needed
    doc_text: str = "",
) -> str:
    """
    Build the LLM prompt and call Groq.
    Competitors are passed as names only — the LLM uses its own
    training knowledge about Adidas, Puma, etc. rather than scraped data.
    """

    # Build Nike context from scraped pages
    nike_context = ""
    for url, content in nike_web_data.items():
        nike_context += f"\n--- Source: {url} ---\n{content[:2000]}\n"

    # Optional uploaded product doc
    doc_section = ""
    if doc_text:
        doc_section = f"\n--- UPLOADED PRODUCT DOCUMENT ---\n{doc_text[:2000]}\n"

    competitors_str = ", ".join(competitor_names) if competitor_names else "Adidas, Under Armour, Puma, New Balance"

    user_prompt = f"""
You are generating a Sales Intelligence One-Pager for a sales rep selling to Nike, Inc.

════════════════════════════════════════
SALES REP'S PRODUCT
════════════════════════════════════════
Product Name       : {product_name}
Product Category   : {product_category}
Value Proposition  : {value_proposition}
Target Contact     : {target_customer}
{doc_section}

════════════════════════════════════════
PROSPECT: NIKE, INC.
Website            : https://www.nike.com
HQ                 : Beaverton, Oregon, USA
Industry           : Sportswear, Footwear, Apparel & Digital Fitness
Ticker             : NKE (NYSE)
════════════════════════════════════════
LIVE DATA SCRAPED FROM NIKE'S WEBSITE:
{nike_context}

NOTE ON COMPETITORS: The following competitors were selected by the sales rep:
{competitors_str}
Use your training knowledge to analyse these competitors — no scraped data needed.

════════════════════════════════════════
YOUR TASK — Generate exactly these 7 sections:
════════════════════════════════════════

## 🏢 COMPANY OVERVIEW — NIKE, INC.
4–5 sentences: business model, revenue scale, key segments (Footwear, Apparel,
Equipment, Digital), and current strategic priorities. Use FY2024 data if available.

## 🎯 NIKE'S STRATEGY RELEVANT TO {product_category.upper()}
Analyse Nike's direction as it relates to {product_category}. Cover:
- Statements from executives (CEO, CDO, CTO, CFO)
- Technology investments and digital transformation signals
- Consumer Direct Acceleration strategy
- Nike Membership, Nike App, SNKRS platform signals
- Any hiring or partnership indicators

## 🥊 COMPETITOR LANDSCAPE — {competitors_str}
Using your knowledge of these competitors:
- Summarise each competitor's technology and digital strategy
- Identify where Nike leads vs lags vs each competitor
- Show where {product_name} creates competitive advantage for Nike

## 👔 KEY STAKEHOLDERS & LEADERSHIP
Nike leaders most relevant to a {product_category} sale:
- Name, Title, and why they matter to this deal
- Any public quotes or earnings-call statements
- Economic buyer / Technical buyer / Champion roles
- Key names: CEO John Donahoe, CFO Matthew Friend, Chief Digital Officer

## 📊 STRATEGIC FIT ANALYSIS
One focused paragraph: why {product_name} is the right fit for Nike RIGHT NOW.
Link Nike's stated priorities directly to: "{value_proposition}"
Be specific — mention Consumer Direct Acceleration, DTC growth, Nike Digital.

## 💬 RECOMMENDED TALKING POINTS FOR {target_customer.upper()}
5 sharp, Nike-specific talking points to open the conversation.
Each must reference a real Nike initiative, metric, or challenge.
No generic enterprise sales language.

## 🔗 SOURCES & FURTHER READING
- Nike Investor Relations : https://investors.nike.com
- Nike Newsroom           : https://about.nike.com/en/newsroom
- Nike Annual Report      : https://investors.nike.com/investors/financial-information/annual-reports
- Nike SEC 10-K           : https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320187&type=10-K
- Nike FY2024 Results     : https://investors.nike.com/investors/news-events-and-reports/press-releases

---
Tone: Confident, precise, actionable. Every sentence must be Nike-specific.
Format: Clean markdown with emoji section headers exactly as shown above.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.35,
        max_tokens=2500,
    )

    return response.choices[0].message.content
