from playwright.sync_api import sync_playwright
import time

# pip install -r requirements.txt
# playwright install

def scrape_page(url: str) -> str | None:
    try:
        with sync_playwright() as p:

            # Launch firefox (you can also use p.Chromium or p.webkit)
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_selector("body")
            html = page.content()

            browser.close()
            return html
            
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


# https://finance.yahoo.com/
# https://www.moneycontrol.com/