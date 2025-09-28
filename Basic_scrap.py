from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup 


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/brave-browser"  #comment if using chrome
driver=webdriver.Chrome(options=chrome_options)  

def scrape_page(url):
    try:
        driver.get(url)
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup.prettify()
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        driver.quit()
