import os
import hashlib
import fitz  # PyMuPDF
import pdfplumber
import docx
import docx2txt
from pptx import Presentation
from PIL import Image
import easyocr
import pandas as pd
import requests

class FileReader:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.reader = easyocr.Reader(['en', 'fa'])

    def download_and_read_files(self, urls):
        if not urls:
            print("No URLs provided.")
            return {}
        for url in urls:
            if url:
                self._download_file(url)
        return self.read_files()

    def _download_file(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.basename(url)
            file_path = os.path.join(self.directory_path, filename)
            with open(file_path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Failed to download file: {url}")

    def read_files(self):
        file_contents = {}
        if not os.path.exists(self.directory_path):
            print(f"Directory does not exist: {self.directory_path}")
            return file_contents

        for filename in os.listdir(self.directory_path):
            file_path = os.path.join(self.directory_path, filename)
            if not os.path.isfile(file_path):
                continue
            if filename == 'extracted_images':  # Skip the 'extracted_images' directory
                continue
            if filename.endswith('.txt'):
                file_contents[filename] = self._read_txt(file_path)
            elif filename.endswith('.pdf'):
                file_contents[filename] = self._read_pdf(file_path)
            elif filename.endswith('.docx'):
                file_contents[filename] = self._read_docx(file_path)
            elif filename.endswith('.pptx'):
                file_contents[filename] = self._read_pptx(file_path)
            elif filename.endswith('.xlsx'):
                file_contents[filename] = self._read_xlsx(file_path)
            elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                file_contents[filename] = self._read_image(file_path)
            else:
                print(f"Unsupported file type: {filename}")
        return file_contents

    def _read_txt(self, file_path):
        if not os.path.isfile(file_path):
            return ""
        with open(file_path, 'r') as file:
            content = file.read()
        return content if content else ""

    def _read_pdf(self, file_path):
        if not os.path.isfile(file_path):
            return {'text': '', 'images': [], 'image_text': ''}

        text = ""
        image_text = ""
        images = []
        image_dir = os.path.join(self.directory_path, 'extracted_images')
        os.makedirs(image_dir, exist_ok=True)

        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                for table in page.extract_tables():
                    text += "Table:\n"
                    for row in table:
                        text += "\t".join(str(cell) if cell is not None else "" for cell in row) + "\n"

        pdf_document = fitz.open(file_path)
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_hash = hashlib.md5(image_bytes).hexdigest()
                image_ext = base_image["ext"]
                image_filename = os.path.join(image_dir, f"{image_hash}.{image_ext}")

                if not os.path.exists(image_filename):
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_bytes)
                    images.append(image_filename)

        for image_path in images:
            image_text += f"\nText from {os.path.basename(image_path)}:\n"
            image_text += self._read_image(image_path)

        return {'text': text, 'images': images, 'image_text': image_text}

    def _read_docx(self, file_path):
        if not os.path.isfile(file_path):
            return ""
        text = docx2txt.process(file_path)
        doc = docx.Document(file_path)
        for table in doc.tables:
            text += "\nTable:\n"
            for row in table.rows:
                text += "\t".join(cell.text if cell.text else "" for cell in row.cells) + "\n"
        return text

    def _read_pptx(self, file_path):
        if not os.path.isfile(file_path):
            return ""
        prs = Presentation(file_path)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text

    def _read_image(self, file_path):
        if not os.path.isfile(file_path):
            return ""
        result = self.reader.readtext(file_path, detail=0)
        return "\n".join(result)

    def _read_xlsx(self, file_path):
        if not os.path.isfile(file_path):
            return ""
        xl = pd.ExcelFile(file_path)
        text = ""
        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            text += f"Sheet: {sheet_name}\n"
            text += df.to_string(index=False)
        return text

# Example usage:
if __name__ == "__main__":
    directory_path = "E:\\Codes\\LLM Apps\\SuperAgent\\Knowledge\\files"
    urls = [
        "https://web.mst.edu/~hilgers/index_files/IST%205001.pdf",
    ]
    reader = FileReader(directory_path)
    contents = reader.download_and_read_files(urls)
    for filename, content in contents.items():
        if isinstance(content, dict) and 'images' in content:
            print(f"Contents of {filename}:\nText:\n{content['text']}\nImages: {content['images']}\nImage Text:\n{content['image_text']}\n")
        else:
            print(f"Contents of {filename}:\n{content}\n")