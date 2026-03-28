# ZNA Backend — AI Career Workspace API

Clean, production-grade Node.js/Express backend powering the ZNA AI Studio.

## Stack
- **Runtime**: Node.js 18+
- **Framework**: Express 4
- **LLM**: Google Gemini 2.0 Flash
- **PDF**: Puppeteer (Chromium headless)
- **Security**: Helmet, CORS, Rate Limiting

---

## Setup

```bash
git clone <repo>
cd zna-backend
npm install
cp .env.example .env     # Fill in your GEMINI_API_KEY
npm run dev
```

---

## API Reference

### Health
| Method | Endpoint  | Description        |
|--------|-----------|--------------------|
| GET    | /health   | System health check |

---

### Resume  `/api/resume`
| Method | Endpoint              | Body                                          | Description                          |
|--------|-----------------------|-----------------------------------------------|--------------------------------------|
| POST   | /parse                | `{ rawText }`                                 | Parse LinkedIn/resume text to JSON   |
| POST   | /generate             | `{ parsedData, targetJobTitle, templateStyle }` | Generate polished resume           |
| POST   | /parse-and-generate   | `{ rawText, targetJobTitle, templateStyle, name, email, phone, github, linkedin }` | Full pipeline |

**Template Styles**: `Standard Corporate` · `Modern Creative` · `Minimal Clean`

---

### Cover Letter  `/api/cover-letter`
| Method | Endpoint   | Body                                         | Description                    |
|--------|------------|----------------------------------------------|--------------------------------|
| POST   | /generate  | `{ resumeData, jobDescription, tone }`       | Generate tailored cover letter |

**Tones**: `professional` · `enthusiastic` · `concise`

---

### ATS Match Engine  `/api/ats`
| Method | Endpoint   | Body                              | Description                        |
|--------|------------|-----------------------------------|------------------------------------|
| POST   | /scan      | `{ resumeData, jobDescription }` | Full ATS scan with score breakdown |
| POST   | /keywords  | `{ jobDescription }`             | Extract keywords from JD           |

**ATS Scan Response:**
```json
{
  "overallScore": 87,
  "breakdown": { "keywordMatch": 90, "skillsAlignment": 85, ... },
  "matchedKeywords": [...],
  "missingKeywords": [...],
  "improvements": [{ "section": "Skills", "suggestion": "Add TypeScript" }],
  "verdict": "Strong Match"
}
```

---

### PDF Export  `/api/pdf`
| Method | Endpoint      | Body                                   | Returns        |
|--------|---------------|----------------------------------------|----------------|
| POST   | /resume       | `{ resumeData, templateStyle }`        | PDF download   |
| POST   | /cover-letter | `{ coverLetterText, applicantName }`   | PDF download   |

---

### Job Portal  `/api/jobs`
| Method | Endpoint             | Body                           | Description                     |
|--------|----------------------|--------------------------------|---------------------------------|
| POST   | /search-suggestions  | `{ targetJobTitle, skills }`  | LinkedIn search URL + tips      |

---

## Project Structure

```
zna-backend/
├── server.js                   # Entry point, middleware, route mount
├── .env.example
├── package.json
├── routes/
│   ├── resume.js               # /api/resume/*
│   ├── coverLetter.js          # /api/cover-letter/*
│   ├── ats.js                  # /api/ats/*
│   ├── pdf.js                  # /api/pdf/*
│   └── jobPortal.js            # /api/jobs/*
└── services/
    ├── llmService.js           # Gemini abstraction layer
    ├── resumeService.js        # Parse + generate resume
    ├── coverLetterService.js   # Cover letter generation
    ├── atsService.js           # ATS scoring + keyword extraction
    └── pdfService.js           # Puppeteer PDF rendering
```
