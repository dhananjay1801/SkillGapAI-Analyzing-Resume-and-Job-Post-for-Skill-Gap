import streamlit as st
from PyPDF2 import PdfReader
import docx2txt

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



def parse_pdf(file):
    file.seek(0)
    try:
        pdf = PdfReader(file)
    except Exception as exc:
        # raise ValueError("Unable to read PDF. It may be encrypted or corrupted.") from exc
        st.error('Failed to read pdf.')

        

    pages_text = []
    for page_no, page in enumerate(pdf.pages, start = 1):
        try:
            page_text = page.extract_text()
        except Exception as exc:
            # raise ValueError(f'Failed to extract text from page {page_no}') from exc
            st.error(f'Failed to extract text from page {page_no}.')

        
        if page_text:
            pages_text.append(page_text)
        else:
            pages_text.append("")
    
    if not pages_text:
        # raise ValueError("No extractable text found in the pdf.")
        st.error('No extractable text found in the pdf.')
    
    return '\n'.join(pages_text).strip()



def parse_docx(file):
    file.seek(0)
    try:
        docx = docx2txt.process(file)
    except Exception as exc:
        # raise ValueError('Failed to read docx file.') from exc
        st.error('Failed to read docx file.')

    if not docx or not docx.strip():
        # raise ValueError("No text found in the docx file.")
        st.error('No text found in the docx file.')
    
    return docx.strip()


def parse_file(file):
    if file is None:
        # raise ValueError('No file uploaded.')
        st.error('No file uploaded.')
    
    filename = file.name.lower()

    if filename.endswith('.txt'):
        return parse_txt(file)

    if filename.endswith('.pdf'):
        return parse_pdf(file)

    if filename.endswith('.docx'):
        return parse_docx(file)

    # raise ValueError("Unsupported file type. Please upload pdf, docx or txt file.")
    st.error('Unsupported file type. Please upload pdf, docx or txt file.')
    