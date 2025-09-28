import time, random, logging
from stem import Signal
from stem.control import Controller
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from fake_useragent import UserAgent

# CONFIG
TOR_SOCKS = "socks5://127.0.0.1:9050"   # Playwright proxy for Tor
CONTROL_PASS = "S3cur3CollegeProjPass"  # Tor control password


# make a UA generator
ua = UserAgent()

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# helpers
def new_tor_identity(password=CONTROL_PASS, wait=5):
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password)
            controller.signal(Signal.NEWNYM)
        logging.info("Requested new Tor circuit.")
        time.sleep(wait)
    except Exception as e:
        logging.warning("Failed to renew Tor identity: %s", e)

def random_sleep(a=1.5, b=4.0):
    time.sleep(random.uniform(a, b))

def human_scroll_and_pause(page, height=2000):
    # scroll in chunks to simulate reading
    viewport_h = page.evaluate("() => window.innerHeight")
    total = height
    step = int(viewport_h * 0.6)
    scrolled = 0
    while scrolled < total:
        page.mouse.wheel(0, step)
        random_sleep(0.5, 1.4)
        scrolled += step

def block_unnecessary_requests(route):
    # block images/fonts/ads to reduce bandwidth and noise (optional)
    if route.request.resource_type in ["font","stylesheet","style","script"]:
        return route.abort()
    return route.continue_()

# main scraping function
def scrape_page(url, rotate_ip_every=3, password=CONTROL_PASS, max_retries=3):
    tries = 0
    while tries < max_retries:
        tries += 1
        try:
            # rotate Tor IP occasionally
            if tries == 1:
                new_tor_identity(password)

            proxy = {"server": TOR_SOCKS}
            # random UA
            user_agent = ua.random

            with sync_playwright() as p:
                # Use persistent context to keep cookies and localStorage between runs
                user_data_dir = "./playwright_profile"
                browser = p.chromium.launch_persistent_context(
                    user_data_dir,
                    # headless=True,
                    proxy=proxy,
                    viewport={"width": 1366, "height": 768},
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        # reduce fingerprint by disabling automation flags - Playwright already helps
                    ],
                    record_video_dir=None,
                )

                page = browser.new_page()
                page.set_extra_http_headers({"User-Agent": user_agent})
                # set timezone / language if needed
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                # route to block heavy resources
                page.route("**/*", lambda route: block_unnecessary_requests(route))

                logging.info("Visiting %s with UA: %s", url, user_agent)
                page.goto(url, timeout=90000)
                page.wait_for_selector("body", timeout=20000)

                # human-like actions
                random_sleep(1.0, 2.5)
                human_scroll_and_pause(page, height=1500)
                # move mouse a bit
                page.mouse.move(random.randint(100, 500), random.randint(100, 300))
                random_sleep(0.5, 1.0)

                html = page.content()
                # parse minimal info: page title & url snapshot
                title = page.title()
                current_url = page.url

                # close context (keeps profile data)
                browser.close()

                logging.info("Success: %s (%d chars)", title, len(html))
                return html

        except PWTimeout as e:
            logging.warning("Playwright timeout, try %s/%s: %s", tries, max_retries, e)
            random_sleep(2, 6)
            new_tor_identity(password)
        except Exception as e:
            logging.exception("Scrape failed attempt %s/%s: %s", tries, max_retries, e)
            random_sleep(2, 6)
            new_tor_identity(password)

    raise RuntimeError("Failed to fetch after retries")


# https://finance.yahoo.com/
# https://www.moneycontrol.com/
# tor --hash-password password:S3cur3CollegeProjPass
# 16:71DC33176DB91D1760BF805A1526C0DC3323DC5573FF96D823D0F6EE99