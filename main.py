import streamlit as st
from scrapping import scrape_page, preprocess_text, split_text


import os
import sys


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.title("LLM web-scrapping Application")
url= st.text_input("Enter the URL to scrape web-page:")

if st.button("Scrape"):
    if url:
        st.write(f"Scraping the web page")
        page_content_soup = scrape_page(url)
        page_content=preprocess_text(page_content_soup)
        split_contents = split_text(page_content, max_length=3000)

        st.session_state['dom']=page_content
        st.session_state['chunks']=split_contents
        st.session_state['html']=page_content_soup

        st.success('web page scraped and processed successfully!')

    else:
        st.error("Please enter a valid URL.")


with st.expander("Show scrapped content"):
    st.text_area("Scrapped Content", value=st.session_state['dom'], height=300)

if "dom" in st.session_state:
    parsed_content=st.text_area("Describe what do you want to Analyze from the scrapped content?", height=100)
    if st.button("Analyze"):
        if parsed_content:
            st.write(f"Analyzing the content for: {parsed_content}")
            # Here you can add your analysis logic using LLMs or any other method

            st.success("Analysis complete!")
        else:
            st.error("Please enter a valid input for analysis.")