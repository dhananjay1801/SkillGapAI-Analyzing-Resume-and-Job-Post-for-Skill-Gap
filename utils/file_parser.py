import streamlit as st
from PyPDF2 import PdfReader
import docx2txt
import easyocr
import fitz

def parse_txt(file):
    file.seek(0)
    try:
        txt = file.read()

        if isinstance(txt, bytes):
            return txt.decode('utf-8')
        return txt

    except Exception as exc:
        # raise ValueError(f"Failed to read text file: {exc}") from exc
        st.error('Failed to read text file.')
        return ""



def parse_pdf(file):
    file.seek(0)
    try:
        pdf = PdfReader(file)
    except Exception as exc:
        # raise ValueError("Unable to read PDF. It may be encrypted or corrupted.") from exc
        st.error('Failed to read pdf.')
        return ""

    pages_text = []
    for page_no, page in enumerate(pdf.pages, start = 1):
        try:
            page_text = page.extract_text()
        except Exception as exc:
            # raise ValueError(f'Failed to extract text from page {page_no}') from exc
            st.error(f'Failed to extract text from page {page_no}.')
            page_text = ""
        
        if page_text:
            pages_text.append(page_text)
        else:
            pages_text.append("")
    
    all_text = '\n'.join(pages_text).strip()
    if not all_text:
        # try OCR if not text layer found (pdf is image based)
        return parse_pdf_ocr(file)
    
    return all_text


def parse_pdf_ocr(file):
    # Extract text from image-based PDF using OCR
    file.seek(0)
    pdf_bytes = file.read()

    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        st.error('Failed to open PDF for OCR.')
        return ""

    reader = easyocr.Reader(['en'], gpu=False)

    pages_text = []
    for page_num in range(len(pdf_document)):
        try:
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")
            
            result = reader.readtext(img_bytes, detail=0)
            text = ' '.join(result)
            pages_text.append(text)
        except Exception as exc:
            st.error(f'OCR failed on page {page_num + 1}.')
            pages_text.append("")

    pdf_document.close()

    all_text = '\n'.join(pages_text).strip()
    if not all_text:
        st.error('OCR could not extract any text from the PDF.')

    return all_text



def parse_docx(file):
    file.seek(0)
    try:
        docx = docx2txt.process(file)
    except Exception as exc:
        # raise ValueError('Failed to read docx file.') from exc
        st.error('Failed to read docx file.')
        return ""

    if not docx or not docx.strip():
        # raise ValueError("No text found in the docx file.")
        st.error('No text found in the docx file.')
    
    return docx.strip()


def parse_file(file):
    if file is None:
        # raise ValueError('No file uploaded.')
        st.error('No file uploaded.')
        return ""
    
    filename = file.name.lower()

    if filename.endswith('.txt'):
        return parse_txt(file)

    if filename.endswith('.pdf'):
        return parse_pdf(file)

    if filename.endswith('.docx'):
        return parse_docx(file)

    # raise ValueError("Unsupported file type. Please upload pdf, docx or txt file.")
    st.error('Unsupported file type. Please upload pdf, docx or txt file.')
    return ""