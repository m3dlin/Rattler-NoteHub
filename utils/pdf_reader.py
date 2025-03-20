"""
This module will contain helper functions to obtain data (PDFs) from Firebase DB.
"""

"""
NOTES: 

- this only works for text based PDFs.
- if i want to add function to extract images, i need to use pdf2image,pytesseract and pillow libraries.
- this will give the website the ability to extract text from images and normal text.


"""

from pypdf import PdfReader
import requests
import os


def download_pdf_from_firebase(pdf_url):
    # download the pdf from the firebase URL (as long as it exists) and download it as a temp file.
    # reminder: pdf_url is the file_path of the note.
    local_pdf_path = "uploads/temp.pdf"    
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(local_pdf_path, "wb") as file:
            file.write(response.content)
        return local_pdf_path
    else:
        raise Exception(f"Failed to download PDF. Status code: {response.status_code}")


def extract_text_from_pdf(pdf_path):
    # extract text from the pdf file, and return it as a string.
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    remove_temp_file()
    return text

# helper function to remove the temp file.
def remove_temp_file():
    # remove the temp file.
    if os.path.exists("uploads/temp.pdf"):
        os.remove("uploads/temp.pdf")

