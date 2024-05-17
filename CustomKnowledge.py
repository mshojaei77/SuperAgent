from Tools.DuckduckgoSearch import SearchTool
from Tools.ArxivLoader import ArxivTool
from Tools.PdfLoader import PdfTool
from Tools.WebLoader import WebTool
from Tools.YoutubeLoader import YoutubeTool
from Tools.SearchPdf import SearchPdfTool
import streamlit as st 


with st.sidebar:
    st.header('Knowledge base', divider='violet')
    ispdf = st.checkbox("Pdf files")
    iswebpage = st.checkbox("Webpages")
    issearch = st.checkbox("Google Search Results")
    isarxiv = st.checkbox("Arxiv Papers")
    isyoutube = st.checkbox("Youtube Videos")