import pdfplumber
import pandas as pd

# Function to extract tables from a PDF
def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables({
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines"
                })
            tables.extend(page_tables)
    return tables

# Path to the PDF file (replace with your actual PDF file path)
pdf_path = '/Users/prakashsethu/Documents/Whole Balance sheets - updated - v2 (v1 errors removed)/Company 1 - Full Balance Sheet - Sheet1 fully tabularized.pdf'

# Extract tables from the PDF
tables = extract_tables_from_pdf(pdf_path)

# Check the first few entries to understand the table structure
for i, table in enumerate(tables):
    print(f"Table {i}:")
    for row in table[:100]:  # Print the first 5 rows of each table
        print(row)
    print()

# Assuming the first table and first row are the headers
# Convert the second table to a DataFrame if it matches your expected structure
df = pd.DataFrame(tables[1][1:], columns=tables[1][0])

# Display the DataFrame
print(df)

# Get the number of rows
num_rows = df.shape[0]
print(f"Number of rows: {num_rows}")