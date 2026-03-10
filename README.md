👟 Nike Sales Intelligence Agent
A Groq + Llama 3.3 70B powered Streamlit app that generates a one-page
sales intelligence brief on Nike, Inc. — including company strategy,
competitor landscape, key stakeholders, and tailored talking points.

🚀 Setup in VS Code (Step-by-Step)
Step 1 — Open the folder in VS Code
File → Open Folder → select the Sales_Assistant_Agent folder

Step 2 — Open the terminal
Press Ctrl + ` (backtick) to open the integrated terminal

Step 3 — Create a virtual environment
bashpython -m venv venv
Step 4 — Activate the virtual environment
bash# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
You should see (venv) appear at the start of the terminal prompt.

Step 5 — Install all dependencies
bashpip install -r requirements.txt

Step 6 — Add your Groq API key

Go to https://console.groq.com and sign up (free)
Click API Keys → Create API Key
Open the .env file in VS Code
Replace gsk_your-key-here with your real key:

GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
Step 7 — Run the app
bashstreamlit run app.py
Your browser will open automatically at http://localhost:8501 🎉

📁 File Structure
Sales_Assistant_Agent/
├── app.py              ← Streamlit UI (main entry point — run this)
├── scraper.py          ← Scrapes Nike + competitor websites
├── llm_engine.py       ← Prompt engineering + Groq API call
├── pdf_generator.py    ← Branded PDF one-pager (ReportLab)
├── requirements.txt    ← All Python dependencies
├── .env                ← Your Groq API key (never commit this!)
└── README.md           ← This file

🧠 How It Works
[Streamlit UI]
     │
     ▼
[scraper.py]  →  Scrapes nike.com, about.nike.com, investor pages
                 + selected competitor sites (Adidas, Puma, etc.)
     │
     ▼
[llm_engine.py] → Sends all scraped text + your product details
                  to Groq (Llama 3.3 70B) with a structured prompt
     │
     ▼
[Report displayed in browser + pdf_generator.py → PDF download]

🔒 Safety Notes

The LLM is constrained via SYSTEM_PROMPT to ONLY produce sales intelligence.
It will not answer general questions or engage in conversation.
Never commit your .env file to GitHub. Add .env to your .gitignore.


🎨 Pre-filled Demo Values
The app ships with these defaults (editable in the sidebar):
FieldDefault ValueProductSnowflake Data CloudCategoryCloud Data Platform & AnalyticsProspectNike, Inc. (nike.com)Target ContactJohn Donahoe, CEOCompetitorsAdidas, Under Armour, Puma

❓ Troubleshooting
ProblemFixModuleNotFoundErrorMake sure venv is active and you ran pip install -r requirements.txtGROQ_API_KEY not foundCheck your .env file has the correct keyScraping returns emptyNike may block scrapers — the LLM will still use its training knowledgeStreamlit not foundRun pip install streamlit manually