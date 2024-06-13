import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import os
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path




logging.basicConfig(level=logging.WARNING)




dir = Path.cwd().absolute()
FILES_DIR = dir / "files"




class DocumentParser:
    def __init__(self, document_path):
        self.document_path = document_path
        self.document_name = os.path.splitext(os.path.basename(document_path))[0]
        try:
            self.doc = fitz.open(document_path)
        except Exception as e:
            logging.error(f"Failed to open document: {e}")




    def fetch_metadata(self):
        try:
            metadata = self.doc.metadata
            title = metadata.get('title')
            if not title:
                title = metadata.get('Title')
            if not title:
                title = self.doc[0].get_text("text").split('\n')[0]
            return title
        except Exception as e:
            logging.error(f"Failed to fetch metadata: {e}")
            return 'Untitled'




    def extract_pdf(self, image_folder):
        text_content = []
        images = []
        links = []
        os.makedirs(image_folder, exist_ok=True)




        for page_num in range(len(self.doc)):
            try:
                page = self.doc.load_page(page_num)
                text = page.get_text()
                paragraphs = text.split('.\n')
                text_content.append((paragraphs, page_num))




                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = self.doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    alt_text = base_image.get("alt")
                    if not alt_text:
                        alt_text = self._find_alt_text(page, img, img_index)








                    shorten = alt_text[:5]
                    name = re.sub(r'\W+', '_', shorten)
                    image_file_name = f"{name}{img_index}.{image_ext}"
                    image_file_path = os.path.join(image_folder, image_file_name)








                    with open(image_file_path, 'wb') as image_file:
                        image_file.write(image_bytes)








                    images.append((image_file_path, page_num, alt_text))








                links.extend([(link['uri'], page_num) for link in page.get_links() if 'uri' in link])
            except Exception as e:
                logging.error(f"Failed to process page {page_num}: {e}")




        return text_content, images, links








    def _find_alt_text(self, page, img, img_index):
        image_rect = fitz.Rect(img[:4])
        y1 = image_rect.y1
        min_distance = float("inf")
        alt_text = None




        for line in page.get_text("dict")["blocks"]:
            if "lines" in line:
                for span in line["lines"]:
                    span_text = span["spans"][0]["text"]
                    if 'figure' in span_text.lower() or 'image' in span_text.lower():
                        return span_text
                    span_rect = fitz.Rect(span["bbox"])
                    if span_rect.y1 > y1 and (span_rect.y1 - y1) < min_distance:
                        min_distance = span_rect.y1 - y1
                        alt_text = span_text




        return alt_text or f"Page{page}_Image{img_index}"




class HTMLGenerator:
    def __init__(self, title, text_content, images, links):
        self.title = title
        self.text_content = text_content
        self.images = images
        self.links = links


    def generate_html(self):
        soup = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")


        soup.head.append(soup.new_tag("title"))
        soup.title.string = self.title


        body = soup.body


        body.append(soup.new_tag("h1"))
        body.h1.string = self.title


        added_images = set()


        for paragraphs, page_num in self.text_content:
            for paragraph in paragraphs:
                p_tag = soup.new_tag("p")


                # Replace URLs with anchor tags
                def replace_urls_with_links(text):
                    return re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', text)


                p_tag.append(BeautifulSoup(replace_urls_with_links(paragraph), "html.parser"))


                # Insert images after each paragraph if any exist on the same page
                for img, img_page_num, alt_text in self.images:
                    if img_page_num == page_num and img not in added_images:
                        p_tag.append("\n")
                        img_tag = soup.new_tag("img", src=img, alt=alt_text)
                        p_tag.append(img_tag)
                        added_images.add(img)


                body.append(p_tag)
                

        return str(soup)


class DocumentConverter:
    def __init__(self, document_path):
        self.document_path = document_path
        self.document_parser = DocumentParser(document_path)


    def convert_to_html_string(self):
        image_folder = os.path.join(os.path.dirname(self.document_path), 'extracted_images')
        title = self.document_parser.fetch_metadata()


        text_content, images, links = self.document_parser.extract_pdf(image_folder)
        html_generator = HTMLGenerator(title, text_content, images, links)
        html_content = html_generator.generate_html()
        return html_content


class DirectoryConvertor:
    def __init__(self, doc_directory=FILES_DIR):
        self.doc_directory = doc_directory


    def process_documents(self):
        import os
        if not os.path.exists(self.doc_directory):
            logging.error(f"Directory not found: {self.doc_directory}")
            return
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._process_single_document, os.path.join(self.doc_directory, filename))
                       for filename in os.listdir(self.doc_directory) if filename.endswith(".pdf")]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Failed to process a document: {e}")


    def _process_single_document(self, document_path):
        try:
            converter = DocumentConverter(document_path)
            html_content = converter.convert_to_html_string()
            html_file_name = os.path.splitext(os.path.basename(document_path))[0] + ".html"
            html_file_path = os.path.join(self.doc_directory, html_file_name)
            with open(html_file_path, "w", encoding="utf-8") as file:
                file.write(html_content)
        except Exception as e:
            logging.error(f"Failed to process document {document_path}: {e}")


# Example usage
if __name__ == "__main__":
    convertor = DirectoryConvertor(doc_directory=FILES_DIR)
    convertor.process_documents()