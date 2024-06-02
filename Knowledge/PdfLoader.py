import os
import requests
import fitz  # PyMuPDF
import sys

from settings import FILES_DIR

class SimplePdfReader:
    def _extract_text_and_images(self, reader):
        text = ""
        images = []
        for page_num in range(len(reader)):
            page = reader.load_page(page_num)
            text += f"Page {page_num + 1}\n" + page.get_text("text") + "\n"
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = reader.extract_image(xref)
                image_bytes = base_image["image"]
                img_extension = base_image["ext"]
                alt_text = img[7] if img[7] else None
                img_filename = os.path.join(FILES_DIR, f"pdf_images/image_page_{page_num + 1}_{img_index}.{img_extension}")
                img_placeholder = f"\n[Image: {os.path.basename(img_filename)}]\n"
                placeholder_index = text.find(f"Image_{img_index}")
                if placeholder_index == -1:
                    text += img_placeholder
                else:
                    text = text[:placeholder_index] + img_placeholder + text[placeholder_index:]
                images.append((img_filename, alt_text))
                os.makedirs(os.path.dirname(img_filename), exist_ok=True)
                with open(img_filename, "wb") as img_file:
                    img_file.write(image_bytes)
        return text.strip(), images

    def extract_text_from_file(self, path):
        reader = fitz.open(path)
        return self._extract_text_and_images(reader)

    def extract_text_from_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            with open('temp.pdf', 'wb') as f:
                f.write(response.content)

            reader = fitz.open('temp.pdf')
            text, images = self._extract_text_and_images(reader)
            os.remove('temp.pdf')
            return text.encode("utf-8", "backslashreplace").decode("utf-8"), images
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
            return "", []

    def extract_text(self, path):
        if os.path.isfile(path):
            return self.extract_text_from_file(path)
        elif path.startswith('http'):
            return self.extract_text_from_url(path)
        else:
            print("Invalid input. Please provide a valid file path or URL.")
            return "", []

if __name__ == "__main__":
    file_path = FILES_DIR + "\input.pdf"
    file_link = "https://web.mst.edu/~hilgers/index_files/IST%205001.pdf"

    extractor = SimplePdfReader()
    text, images = extractor.extract_text(file_path)
    print("-------local: ")
    print(text)
    print("-------images: ")
    print(images)
    
'''    text2 = extractor.extract_text(file_link)
    print("-----------from link: ")
    print(text2)'''