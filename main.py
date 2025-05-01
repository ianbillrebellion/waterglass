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
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = await context.new_page()
        try:
            await page.goto(data.url, timeout=60000)
            await page.wait_for_selector("table.ms-listviewtable", timeout=20000)

            # Extract links to each event
            event_links = await page.eval_on_selector_all(
                "table.ms-listviewtable a",
                "els => els.map(e => e.href).filter(href => href.includes('EventDispForm.aspx'))"
            )

            for link in event_links:
                event_page = await context.new_page()
                try:
                    await event_page.goto(link, timeout=30000)
                    await event_page.wait_for_selector("body", timeout=10000)

                    # Scrape content from detail page
                    event_data = {
                        "eventName": await event_page.locator("h1").inner_text() if await event_page.locator("h1").count() else "",
                        "date": await event_page.locator("span[title*='Date']").inner_text() if await event_page.locator("span[title*='Date']").count() else "",
                        "description": await event_page.locator("div.ms-rtestate-field").inner_text() if await event_page.locator("div.ms-rtestate-field").count() else "",
                        "eventLink": link
                    }
                    results.append(event_data)
                except Exception as e:
                    results.append({"error": str(e), "eventLink": link})
                finally:
                    await event_page.close()

            await browser.close()
            return {"events": results}

        except Exception as e:
            await browser.close()
            return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


