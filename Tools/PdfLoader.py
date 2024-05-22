import json
import os
from pypdf import PdfReader
import fitz  # PyMuPDF

class PdfTool:
    def __init__(self, file_name):
        self.pdf_path = os.path.join(os.path.dirname(__file__), "pdf_files" , file_name)
        self.pdf_reader = PdfReader(self.pdf_path)
        self.doc = fitz.open(self.pdf_path)

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
    file_name = "sample.pdf"
    extractor = PdfTool(file_name)
    print(extractor.extract_text())