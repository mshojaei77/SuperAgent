import json
import os
from pypdf import PdfReader
import fitz  # PyMuPDF
import requests

class PdfTool:
    def __init__(self, pdf_link):
        self.pdf_path = self.get_pdf_path(pdf_link)
        self.pdf_reader = PdfReader(self.pdf_path)
        self.doc = fitz.open(self.pdf_path)

    def get_pdf_path(self, pdf_link):
        if pdf_link.startswith('http'):
            response = requests.get(pdf_link)
            file_path = "temp_downloaded_pdf.pdf"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
        else:
            return pdf_link

    def extract_text(self):
        text = ""
        for page in self.pdf_reader.pages:
            text += page.extract_text()
        return text

    def extract_images(self):
        images = []
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            images.extend(page.get_images(full=True))
        return images

    def extract_tables(self):
        tables = []
        for page in self.doc:
            tables.extend(page.get_text("dict")["blocks"])
        return [block for block in tables if "lines" in block]

    def extract_metadata(self):
        return self.pdf_reader.metadata

    def extract_all(self):
        return {
            "text": self.extract_text(),
            "images": self.extract_images(),
            "tables": self.extract_tables(),
            "metadata": self.extract_metadata()
        }

if __name__ == "__main__":
    pdf_link = "E:\\Codes\\LLM Apps\\SuperAgent\\Tools\\pdf_files\\python.pdf"
    # pdf_link = "https://www.download.com/python.pdf"  # For URL-based PDF
    extractor = PdfTool(pdf_link)
    print(extractor.extract_text())