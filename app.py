import streamlit as st
import os
import time
import io
from dotenv import load_dotenv
import PyPDF2

from scraper import scrape_nike_pages, NIKE_COMPETITORS
from llm_engine import generate_nike_report
from pdf_generator import generate_pdf

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nike Sales Intelligence Agent",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700;800&family=Barlow+Condensed:wght@600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Barlow', sans-serif; color: #111111; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #F5F5F5 100%);
}
section[data-testid="stSidebar"] * { color: #111111 !important; }

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stTextArea textarea,
section[data-testid="stSidebar"] .stSelectbox select {
    background: rgba(0,0,0,0.04) !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
    color: #111111 !important;
    border-radius: 6px !important;
    font-family: 'Barlow', sans-serif !important;
}
section[data-testid="stSidebar"] label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    color: #FF6600 !important;
}
section[data-testid="stSidebar"] .stCheckbox label {
    font-size: 0.82rem !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    color: #333333 !important;
}

/* ── Main area ── */
.main .block-container { padding-top: 1.8rem; max-width: 920px; }

/* Hero */
.hero {
    background: #111111;
    border-radius: 12px;
    padding: 2.4rem 2.8rem;
    margin-bottom: 1.8rem;
    border-left: 5px solid #FF6600;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: "JUST DO IT.";
    position: absolute;
    right: 2rem; bottom: 1rem;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: rgba(255,255,255,0.04);
    letter-spacing: 0.05em;
}
.hero .eyebrow {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #FF6600;
    margin-bottom: 10px;
}
.hero h1 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    color: #F5F5F5 !important;
    margin: 0 0 0.5rem 0 !important;
    letter-spacing: 0.02em !important;
    line-height: 1.1 !important;
    text-transform: uppercase !important;
}
.hero p {
    color: #999999 !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
    font-weight: 400 !important;
    max-width: 600px !important;
}

/* Feature cards */
.feat-card {
    background: #F7F7F7;
    border-radius: 10px;
    padding: 1.3rem 1.4rem;
    border-top: 3px solid #FF6600;
    height: 100%;
}
.feat-card .icon { font-size: 1.6rem; margin-bottom: 8px; }
.feat-card .title { font-weight: 700; color: #111; margin-bottom: 4px; font-size: 0.95rem; }
.feat-card .desc  { font-size: 0.82rem; color: #666; line-height: 1.5; }

/* Generate button */
div[data-testid="stButton"] > button {
    background: #FF6600 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    font-family: 'Barlow', sans-serif !important;
    transition: background 0.2s ease !important;
}
div[data-testid="stButton"] > button:hover {
    background: #e55a00 !important;
}

/* Report wrapper */
.report-wrap {
    background: #FAFAFA;
    border: 1px solid #E8E8E8;
    border-top: 4px solid #FF6600;
    border-radius: 10px;
    padding: 2rem 2.5rem;
    margin-top: 1.5rem;
}
.report-wrap h2 {
    color: #FF6600 !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    margin-top: 1.5rem !important;
    padding-bottom: 5px !important;
    border-bottom: 1.5px solid #EEEEEE !important;
}

/* Meta chips */
.chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1.2rem; }
.chip  {
    background: #FFF0E6; border: 1px solid #FFBB88;
    color: #CC4400; border-radius: 4px;
    padding: 3px 12px; font-size: 0.78rem; font-weight: 600;
    letter-spacing: 0.03em;
}

/* Status log */
.log { font-family: monospace; font-size: 0.78rem; color: #FF6600; padding: 3px 0; }

hr.divider {
    border: none; border-top: 1px solid rgba(0,0,0,0.10); margin: 0.8rem 0;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1rem 0;">
      <div style="font-size:2rem;">👟</div>
      <div style="font-family:'Barlow Condensed',sans-serif; font-size:1.2rem;
                  font-weight:800; color:#111111; letter-spacing:0.05em;
                  text-transform:uppercase;">Nike Intel Agent</div>
      <div style="font-size:0.72rem; color:#444444; margin-top:2px;">
        Powered by Groq · Llama 3.3 70B
      </div>
    </div>
    <hr class="divider">
    """, unsafe_allow_html=True)

    st.markdown("**YOUR PRODUCT**")

    product_name = st.text_input(
        "Product Name",
        value="Snowflake Data Cloud",
        help="The product you are selling to Nike."
    )
    product_category = st.text_input(
        "Product Category",
        value="Cloud Data Platform & Analytics",
        help="One phrase describing what your product does."
    )
    value_proposition = st.text_area(
        "Value Proposition",
        value=(
            "Unify Nike's fragmented data across DTC, wholesale, and supply chain "
            "into a single governed cloud platform — enabling real-time personalisation, "
            "faster merchandising decisions, and AI-ready analytics at scale."
        ),
        height=110,
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**NIKE PROSPECT**")

    company_url = st.text_input(
        "Company URL",
        value="https://www.nike.com",
        disabled=True,
        help="Fixed to Nike for this demo.",
    )
    target_customer = st.text_input(
        "Target Contact",
        value="John Donahoe, CEO — Nike, Inc.",
        help="The person you are trying to sell to."
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**COMPETITORS TO ANALYSE**")

    selected_competitors = []
    for name in NIKE_COMPETITORS:
        if st.checkbox(name, value=name in ["Adidas", "Under Armour", "Puma"]):
            selected_competitors.append(name)

    extra_competitors = st.text_area(
        "Add more competitors (one name per line)",
        placeholder="Skechers\nAsics\nOn Running",
        height=70,
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**OPTIONAL**")

    uploaded_file = st.file_uploader(
        "Upload Product Overview (PDF)",
        type=["pdf"],
        help="A product deck or one-pager to give the AI more context.",
    )

    api_key_input = st.text_input(
        "Groq API Key (if not in .env)",
        type="password",
        placeholder="gsk_...",
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    generate_btn = st.button("⚡ Generate Nike Intel Report")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="eyebrow">👟 Nike Account Intelligence · B2B Sales Tool</div>
  <h1>Sales Intelligence Agent</h1>
  <p>Instantly generate a one-page account brief on Nike — covering company strategy,
  competitor landscape, key stakeholders, and AI-crafted talking points tailored to
  your product and target contact.</p>
</div>
""", unsafe_allow_html=True)

if not generate_btn:
    c1, c2, c3 = st.columns(3)
    cards = [
        ("🔍", "Live Web Research",
         "Scrapes Nike.com, about.nike.com, investor pages, and competitor sites in real time."),
        ("🧠", "AI-Powered Analysis",
         "Llama 3.3 70B on Groq analyses Nike's strategy and maps it to your product."),
        ("📄", "PDF One-Pager",
         "Download a branded, print-ready intelligence brief to share with your team."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], cards):
        with col:
            st.markdown(f"""
            <div class="feat-card">
              <div class="icon">{icon}</div>
              <div class="title">{title}</div>
              <div class="desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ How to use this tool"):
        st.markdown("""
        1. **Review the sidebar** — product details are pre-filled for a Snowflake → Nike demo.
           Change them to match your actual product.
        2. **Select competitors** — tick the ones you want analysed.
        3. **Add your Groq API key** — either in `.env` or paste it in the sidebar.
        4. **Click ⚡ Generate** — the app scrapes live data, sends it to the LLM, and renders
           your report in ~15–30 seconds.
        5. **Download the PDF** — a branded one-pager is ready to share.
        """)

# ─────────────────────────────────────────────────────────────────────────────
# GENERATION
# ─────────────────────────────────────────────────────────────────────────────
if generate_btn:

    # ── API key ────────────────────────────────────────────────────────────────
    if api_key_input:
        os.environ["GROQ_API_KEY"] = api_key_input
    if not os.getenv("GROQ_API_KEY"):
        st.error("❌ No Groq API key found. Add it to .env or paste it in the sidebar.")
        st.stop()

    # ── Parse uploaded PDF ─────────────────────────────────────────────────────
    doc_text = ""
    if uploaded_file:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            doc_text = " ".join(p.extract_text() or "" for p in reader.pages)[:3000]
        except Exception:
            st.warning("⚠️ Could not parse the uploaded PDF — continuing without it.")

    # ── Progress UI ────────────────────────────────────────────────────────────
    ph = st.empty()
    with ph.container():
        st.markdown("#### 🔄 Building your Nike Intel Report…")
        bar    = st.progress(0)
        status = st.empty()

        def log(msg: str, pct: int):
            status.markdown(f'<div class="log">▸ {msg}</div>', unsafe_allow_html=True)
            bar.progress(pct)
            time.sleep(0.2)

        log("Scraping Nike.com, about.nike.com, investor pages…", 15)
        nike_data = scrape_nike_pages()

        # Merge selected + any extra competitors typed in — names only, no scraping
        all_competitors = list(selected_competitors)
        if extra_competitors.strip():
            extras = [c.strip() for c in extra_competitors.strip().split("\n") if c.strip()]
            all_competitors.extend(extras)

        log(f"Passing competitors to LLM: {', '.join(all_competitors) or 'default set'}…", 40)

        log("Sending data to Groq (Llama 3.3 70B) for analysis…", 60)
        try:
            report_md = generate_nike_report(
                product_name=product_name,
                product_category=product_category or product_name,
                value_proposition=value_proposition or f"{product_name} delivers best-in-class solutions.",
                target_customer=target_customer,
                nike_web_data=nike_data,
                competitor_names=all_competitors,
                doc_text=doc_text,
            )
        except Exception as e:
            ph.empty()
            st.error(f"❌ Groq API error: {e}")
            st.stop()

        log("Rendering branded PDF one-pager…", 82)
        pdf_bytes = generate_pdf(
            report_markdown=report_md,
            product_name=product_name,
            company_url="https://www.nike.com",
            target_customer=target_customer,
        )

        bar.progress(100)
        status.markdown('<div class="log" style="color:#22c55e;">✔ Report ready!</div>',
                        unsafe_allow_html=True)
        time.sleep(0.6)

    ph.empty()

    # ── Meta chips ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="chips">
      <span class="chip">📦 {product_name}</span>
      <span class="chip">🌐 nike.com</span>
      <span class="chip">👤 {target_customer}</span>
      {''.join(f'<span class="chip">🥊 {c}</span>' for c in all_competitors[:4])}
    </div>
    """, unsafe_allow_html=True)

    # ── Report display ─────────────────────────────────────────────────────────
    st.markdown('<div class="report-wrap">', unsafe_allow_html=True)
    st.markdown(report_md)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Download ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    dl_col, _ = st.columns([1, 2])
    with dl_col:
        st.download_button(
            label="📥 Download PDF One-Pager",
            data=pdf_bytes,
            file_name=f"Nike_Sales_Intel_{product_name.replace(' ','_')}.pdf",
            mime="application/pdf",
        )
