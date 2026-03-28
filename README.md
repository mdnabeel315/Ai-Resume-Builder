# 🧠 AI Career Studio

An Apple-inspired, production-grade career toolkit built with **Streamlit** + **Google Gemini 2.0 Flash**.

## Features

| Module | Description |
|---|---|
| 📄 Smart Resume Builder | Auto-parse LinkedIn/raw text or fill a form → AI generates ATS-optimised resume |
| ✉️ Cover Letter Generator | One-click personalised cover letters from your resume memory |
| 🔍 ATS Match Engine | Semantic NLP score, keyword gap analysis, one-click tailoring |
| 🗂️ Overview Dashboard | Live system logs, ATS trend chart, quick-action cards |

## Setup

```bash
# 1. Clone
git clone https://github.com/your-username/ai-career-studio.git
cd ai-career-studio

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

## API Key

Enter your **Gemini API key** directly in the sidebar (no `.env` needed for local use).

For Streamlit Cloud deployment, add it as a secret:

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "AIza..."
```

Then in `app.py` the key is automatically picked up via `os.environ.get("GEMINI_API_KEY")`.

## Deployment (Streamlit Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → set `app.py` as the entry point
4. Add `GEMINI_API_KEY` in the Secrets panel
5. Deploy ✅

## Project Structure

```
ai-career-studio/
├── app.py              # Single-file Streamlit application
├── requirements.txt    # Python dependencies
└── README.md
```

## Tech Stack

- **Frontend/Backend**: Streamlit
- **AI**: Google Gemini 2.0 Flash (`google-generativeai`)
- **PDF Export**: fpdf2
- **Parsing**: Built-in `json` + `re`
