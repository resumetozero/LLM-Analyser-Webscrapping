import streamlit as st
from scrapping import scrape_page
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.title("LLM web-scrapping Application")
url= st.text_input("Enter the URL to scrape web-page:")

if st.button("Scrape"):
    if url:
        st.write(f"Scraping the web page at: {url}")
        # Here you would add the code to scrape the web page and process it with LLM
        page_content_soup = scrape_page(url)
        if page_content_soup:
            print(page_content_soup)
    else:
        st.error("Please enter a valid URL.")
