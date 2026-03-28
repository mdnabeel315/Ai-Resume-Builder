# ZNA AI Studio — Clean Python Backend

Streamlit app with a fully rewritten, production-grade Python backend.

## What was fixed
| Problem | Fix |
|---|---|
| Slow AI responses | Tenacity retry + TTL cache — identical prompts never re-call Gemini |
| Broken / ugly PDFs | ReportLab Platypus with 3 professional themed templates |
| Inaccurate ATS scores | 4-dimension weighted scoring at temperature 0.15 |
| No proper API structure | Clean service layer — `backend/` package with single `__init__.py` |

## Project Structure
```
zna-streamlit/
├── app.py                          # Entry point — Overview Dashboard
├── state_manager.py                # Centralised session state helpers
├── requirements.txt
├── .streamlit/
│   └── secrets.toml.example        # Copy → secrets.toml, add your key
├── backend/
│   ├── __init__.py                 # Public API — import from here
│   ├── llm_service.py              # Gemini abstraction + cache + retry
│   ├── resume_service.py           # Parse + generate resume
│   ├── ats_service.py              # Semantic ATS scan
│   ├── cover_letter_service.py     # Cover letter generation
│   └── pdf_service.py              # ReportLab PDF rendering
└── pages/
    ├── 1_Smart_Resume_Builder.py
    ├── 2_Cover_Letter_Generator.py
    └── 3_ATS_Match_Engine.py
```

## Setup

### Local
```bash
git clone <repo>
cd zna-streamlit
pip install -r requirements.txt

# Add your Gemini key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml and paste your GEMINI_API_KEY

streamlit run app.py
```

### Streamlit Cloud (your current host)
1. Push this folder to your GitHub repo
2. Go to your app → **Settings → Secrets**
3. Add:
   ```
   GEMINI_API_KEY = "your_key_here"
   ```
4. Redeploy

## How to use the backend in a new page

```python
# Any new page — just import from backend
from backend import parse_and_generate, run_ats_scan, generate_resume_pdf
from state_manager import get_resume, set_resume, has_resume

resume = get_resume()          # None if not yet generated
if has_resume():
    pdf = generate_resume_pdf(resume, "Modern Creative")
```
