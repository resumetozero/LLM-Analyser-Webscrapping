import streamlit as st
from scrapping import scrape_page
from bs4 import BeautifulSoup
import re
import pandas as pd


import os
import sys


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.title("LLM web-scrapping Application")
url= st.text_input("Enter the URL to scrape web-page:")

if st.button("Scrape"):
    if url:
        st.write(f"Scraping the web page at: {url}")
        page_content_soup = scrape_page(url)
        soup = BeautifulSoup(page_content_soup, 'html.parser')
        page_content = soup.prettify()

        # Preprocess and save text
        def preprocess_text(html):
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.prettify()
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(text)
            return 'Text preprocessed and saved to output.txt'

        msg = preprocess_text(page_content)
        st.success(msg)

    else:
        st.error("Please enter a valid URL.")


