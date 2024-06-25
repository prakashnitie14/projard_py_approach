import pandas as pd
import pdfplumber


pdf_path = '/Users/prakashsethu/Documents/Whole Balance sheets - updated - v2 (v1 errors removed)/Company 1 - Full Balance Sheet - Sheet1-9.pdf'

# Example for PDF extraction
def extract_pdf_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        tables = first_page.extract_tables()
    return text, tables

# Example for Excel extraction
def extract_excel_data(excel_path):
    df = pd.read_excel(excel_path, sheet_name=None)
    return df
