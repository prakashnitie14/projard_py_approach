import pdfplumber

# Function to extract text and coordinates from a specific page
def extract_text_and_coords(pdf_path, page_number):
    with pdfplumber.open(pdf_path) as pdf:
        if page_number < len(pdf.pages):
            page = pdf.pages[page_number]
            print(f"Page {page_number + 1}")
            for word in page.extract_words():
                print(f"Word: {word['text']}, Coords: ({word['x0']}, {word['top']}, {word['x1']}, {word['bottom']})")
        else:
            print("Invalid page number")

# Path to the PDF file (replace with your actual PDF file path)
pdf_path = '/Users/prakashsethu/Documents/Whole Balance sheets - updated - v2 (v1 errors removed)/Company 1 - Full Balance Sheet - Sheet1 with borders.pdf'
page_number = 2  # Page number to extract from (0-indexed)

# Extract text and coordinates from the specified page
extract_text_and_coords(pdf_path, page_number)