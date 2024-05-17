import json
from pathlib import Path
from pypdf import PdfReader
import fitz  # PyMuPDF

class PdfTool:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_reader = PdfReader(pdf_path)
        self.doc = fitz.open(pdf_path)

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
    
    

if __name__ == "__main__":
    pdf_path = Path(__file__).parent / "pdf_files" / "sample.pdf"
    extractor = PdfTool(pdf_path)
    print(extractor.extract_text())
    print(extractor.extract_images())
    print(extractor.extract_metadata())
    print(extractor.extract_tables())

pdf_path = Path(__file__).parent / "pdf_files"