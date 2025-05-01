# Render Scraper API

A lightweight FastAPI-based scraper that uses Playwright to fetch JavaScript-rendered content (e.g., page titles).

## Deploy Instructions

1. Push this repo to GitHub
2. Create a new **Web Service** on [Render](https://render.com/)
3. Use Python 3.10+
4. Set the **Start Command** to:

```
playwright install && uvicorn main:app --host 0.0.0.0 --port 8000
```

5. Call the API at:

```
POST /scrape
{ "url": "https://example.com" }
```