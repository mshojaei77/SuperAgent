import os
import requests
from pypdf import PdfReader as PyPdfReader
import sys

from settings import FILES_DIR

class SimplePdfReader:
    def extract_text_from_file(self, path):
        reader = PyPdfReader(path)
        text = ""
        for page_num, page in enumerate(reader.pages, start=1):
            text += f"Page {page_num}\n" + page.extract_text() + "\n"
        return text.strip()

    def extract_text_from_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            with open('temp.pdf', 'wb') as f:
                f.write(response.content)

            reader = PyPdfReader('temp.pdf')
            texts = ""
            for page_num, page in enumerate(reader.pages, start=1):
                texts += f"[Page {page_num}]\n" + page.extract_text() + "\n\n"
            os.remove('temp.pdf')
            return texts.strip().encode("utf-8", "backslashreplace").decode("utf-8")
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
            return ""

    def extract_text(self, path):
        if os.path.isfile(path):
            return self.extract_text_from_file(path)
        elif path.startswith('http'):
            return self.extract_text_from_url(path)
        else:
            print("Invalid input. Please provide a valid file path or URL.")
            return ""

if __name__ == "__main__":
    file_path = FILES_DIR + "\sample.pdf"
    file_link = "https://web.mst.edu/~hilgers/index_files/IST%205001.pdf"

    extractor = SimplePdfReader()
    text = extractor.extract_text(file_path)
    print("-------local: ")
    print(text)
    
'''    text2 = extractor.extract_text(file_link)
    print("-----------from link: ")
    print(text2)'''