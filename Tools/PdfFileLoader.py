from langchain_community.document_loaders import PyPDFLoader


class PDFLoader:
    def __init__(self, file_name):
        self.file_name = file_name
        self.loader = PyPDFLoader(self.file_name)

    def load_and_split(self):
        return self.loader.load_and_split()

# Usage
file_name = "example.pdf"
pdf_loader = PDFLoader(file_name)
pages = pdf_loader.load_and_split()


#converting to txt
'''f = open("example.txt", "w", encoding="utf-8")
for page in pages:
    f.write(str(page.page_content).encode('utf-8', 'replace').decode('utf-8'))
    f.write("------\n")
    f.write(str(page.metadata))'''