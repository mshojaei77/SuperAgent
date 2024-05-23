import os
from pypdf import PdfReader
import requests

class PdfReader:
    def extract_text(self, path):
        if os.path.isfile(path):
            reader = PdfReader(path)
            text = ""
            page_num = 1
            for page in reader.pages:
                text += f"Page {page_num}\n" + page.extract_text() + "\n"  # Assuming extract_text exists on page objects
                page_num += 1
        elif path.startswith('http'):
            # URL
            try:
                response = requests.get(path, timeout=10)
                response.raise_for_status()

                with open('temp.pdf', 'wb') as f:
                    f.write(response.content)

                pdf_file = open('temp.pdf', 'rb')
                reader = PdfReader(pdf_file)
                texts = ""
                page_num = 1
                for page in reader.pages:
                    texts += f"[Page {page_num}]\n" + page.extract_text() + "\n\n"
                    page_num += 1
                text = texts.encode("utf-8", "backslashreplace").decode("utf-8")
                pdf_file.close()
                os.remove('temp.pdf')
            except requests.exceptions.RequestException as err:
                print(f"An error occurred: {err}")
                return ""
        else:
            print("Invalid input. Please provide a valid file path or URL.")
            return ""

        return text.strip()

if __name__ == "__main__":
    file_path = "E:\\Codes\\LLM Apps\\SuperAgent\\Tools\\pdf_files\\python.pdf"
    file_link = "https://web.mst.edu/~hilgers/index_files/IST%205001.pdf"

    extractor = PdfReader()
    text2 = extractor.extract_text(file_link)
    print(text2)

    text = extractor.extract_text(file_path)
    print(text)