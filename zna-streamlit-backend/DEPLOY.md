# 🚀 Deployment Guide - ZNA AI Resume Studio

## Streamlit Cloud (Recommended - Free, Instant)

1. **GitHub Push**:
```
git init
git add .
git commit -m \"Production backend + file upload ready\"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

2. **Deploy**:
- https://share.streamlit.io/
- New app → Connect GitHub repo → Select `app.py`
- **Secrets** (Advanced): 
```
GEMINI_API_KEY = your_api_key_here
```

**Live URL**: `https://your-app-name.streamlit.app`

## Production Options

### Heroku
```
# Add Procfile
echo 'web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0' > Procfile
git add Procfile
git commit -m 'Add Heroku Procfile'
git push heroku main
```

### Render.com (Free Tier)
- New Web Service → GitHub repo
- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

### Docker (Self-host)
```
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD [\"streamlit\", \"run\", \"app.py\", \"--server.port=8501\", \"--server.address=0.0.0.0\"]
```
`docker build -t resume-ai . && docker run -p 8501:8501 resume-ai`

## Required Secrets
```
GEMINI_API_KEY=your_gemini_key
```

