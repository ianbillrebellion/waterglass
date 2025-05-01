from fastapi import FastAPI
from pydantic import BaseModel
from playwright.async_api import async_playwright
import uvicorn

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "Scraper API is live"}

@app.post("/scrape")
async def scrape_page(data: ScrapeRequest):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        try:
            await page.goto(data.url, timeout=45000)
            await page.wait_for_selector("body", timeout=10000)  # Adjust to something unique if known
            content = await page.title()
            await browser.close()
            return {"title": content}
        except Exception as e:
            await browser.close()
            return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

