from fastapi import FastAPI
from pydantic import BaseModel
from playwright.async_api import async_playwright
import uvicorn

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape")
async def scrape_event_links(data: ScrapeRequest):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(data.url, timeout=60000)
            await page.wait_for_selector("table.ms-listviewtable", timeout=15000)

            # Extract event detail URLs from anchor tags
            links = await page.eval_on_selector_all(
                'table.ms-listviewtable a[href*="EventDispForm.aspx?ID="]',
                'elements => elements.map(el => el.href)'
            )

            await browser.close()
            return { "events": links }

        except Exception as e:
            await browser.close()
            return { "error": str(e) }

@app.get("/")
async def root():
    return { "message": "Scraper API is live" }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
