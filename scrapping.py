import asyncio
import random
import logging
from stem import Signal
from stem.control import Controller
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

# CONFIG
TOR_SOCKS = "socks5://127.0.0.1:9050"
CONTROL_PASS = "S3cur3CollegeProjPass"

# UA generator
ua = UserAgent()

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ---------- Helpers ----------

async def new_tor_identity(password=CONTROL_PASS, wait=5):
    """Request new Tor circuit asynchronously using asyncio.to_thread"""
    def renew():
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password)
                controller.signal(Signal.NEWNYM)
            logging.info("Requested new Tor circuit.")
        except Exception as e:
            logging.warning("Failed to renew Tor identity: %s", e)
    await asyncio.to_thread(renew)
    await asyncio.sleep(wait)

async def random_sleep(a=1.5, b=4.0):
    await asyncio.sleep(random.uniform(a, b))

async def human_scroll_and_pause(page, height=2000):
    viewport_h = await page.evaluate("() => window.innerHeight")
    total = height
    step = int(viewport_h * 0.6)
    scrolled = 0
    while scrolled < total:
        await page.mouse.wheel(0, step)
        await random_sleep(0.5, 1.4)
        scrolled += step

async def block_unnecessary_requests(route):
    if route.request.resource_type in ["font","stylesheet","style","script"]:
        await route.abort()
    else:
        await route.continue_()

# ---------- Scraping Function ----------

async def scrape_page_async(url, rotate_ip_every=3, password=CONTROL_PASS, max_retries=3):
    tries = 0
    while tries < max_retries:
        tries += 1
        try:
            if tries == 1:
                await new_tor_identity(password)

            proxy = {"server": TOR_SOCKS}
            user_agent = ua.random

            async with async_playwright() as p:
                user_data_dir = "./playwright_profile"
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=True,
                    proxy=proxy,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )

                page = await browser.new_page()
                await page.set_extra_http_headers({"User-Agent": user_agent})
                await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                await page.route("**/*", block_unnecessary_requests)

                logging.info("Visiting %s with UA: %s", url, user_agent)
                await page.goto(url, timeout=90000)
                await page.wait_for_selector("body", timeout=20000)

                # human-like actions
                await random_sleep(1.0, 2.5)
                await human_scroll_and_pause(page, height=1500)
                await page.mouse.move(random.randint(100, 500), random.randint(100, 300))
                await random_sleep(0.5, 1.0)

                html = await page.content()
                title = await page.title()

                await browser.close()
                logging.info("Success: %s (%d chars)", title, len(html))
                return html

        except PWTimeout as e:
            logging.warning("Playwright timeout, try %s/%s: %s", tries, max_retries, e)
            await random_sleep(2, 6)
            await new_tor_identity(password)
        except Exception as e:
            logging.exception("Scrape failed attempt %s/%s: %s", tries, max_retries, e)
            await random_sleep(2, 6)
            await new_tor_identity(password)

    raise RuntimeError("Failed to fetch after retries")

# ---------- Text Processing ----------

def preprocess_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator="\n")
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return text

def split_text(text, max_length=1000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]
