import re
import pandas as pd
import pdfplumber

# Function to extract text from specific pages
def extract_text_from_pdf(pdf_path, page_numbers):
    text_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in page_numbers:
            if page_number <= len(pdf.pages):
                page = pdf.pages[page_number - 1]
                text_data.append(page.extract_text())
    return "\n".join(text_data)  # Concatenate all text into a single string

def analyze_text(text):
    lines = text.split('\n')
    
    # Initialize variables to store the findings
    company_name = ""
    quality_of_statements = ""
    
    # Patterns to search for the quality of financial statements
    audit_pattern = re.compile(r'\baudited financial statements\b', re.IGNORECASE)
    review_pattern = re.compile(r'\breview engagement financial statements\b', re.IGNORECASE)
    compilation_pattern = re.compile(r'\bcompilation engagement financial statements\b', re.IGNORECASE)
    
    # Iterate through each line of the text
    for line in lines:
        # Identify company name (assuming it's one of the first lines or has specific keywords)
        if "Inc." in line or "LLC" in line or "Corp." in line:
            company_name = line.strip()
        
        # Determine the quality of the financial statement
        if audit_pattern.search(line):
            quality_of_statements = "Audited"
        elif review_pattern.search(line):
            quality_of_statements = "Review Engagement"
        elif compilation_pattern.search(line):
            quality_of_statements = "Compilation Engagement"
    
    return company_name, quality_of_statements


def extract_columns_regex(data):
    # Define the adjusted regex patterns to handle various row formats
    pattern_numeric = re.compile(r'(.+?)\s*([\$€£¥₹]?)\s*(-?\$?\(?[\d,]+(?:\.\d{1,2})?\)?)\s*([\$€£¥₹]?)\s*(-?\$?\(?[\d,]+(?:\.\d{1,2})?\)?)')
    pattern_text_date = re.compile(r'(.+?)\s+(\d{2}-\w{3}-\d{4}|\d{4}-\d{2}-\d{2}|\w{3} \d{2}, \d{4})\s+(\d{2}-\w{3}-\d{4}|\d{4}-\d{2}-\d{2}|\w{3} \d{2}, \d{4})')
    structured_data = []

    for row in data:
        match_text_date = pattern_text_date.match(row)
        match_numeric = pattern_numeric.match(row)
        
        if match_text_date:
            parameter = match_text_date.group(1).strip()
            current_year = match_text_date.group(2)
            previous_year = match_text_date.group(3)
            structured_data.append((parameter, '', current_year, '', previous_year))
        
        elif match_numeric:
            parameter = match_numeric.group(1).strip()
            currency1 = match_numeric.group(2)
            current_year = match_numeric.group(3).replace(',', '').replace('$','').replace('€','').replace('£','').replace('¥','').replace('₹','').replace('(','').replace(')','')
            currency2 = match_numeric.group(4)
            previous_year = match_numeric.group(5).replace(',', '').replace('$','').replace('€','').replace('£','').replace('¥','').replace('₹','').replace('(','').replace(')','')

            # Convert to float if valid numeric format
            try:
                current_year = float(current_year)
                previous_year = float(previous_year)
                structured_data.append((parameter, currency1, current_year, currency2, previous_year))
            except ValueError as e:
                print(f"Error converting values: {e}")
        
        elif row.strip():  # Handle cases where parameter is filled but current and previous years are blank
            structured_data.append((row.strip(), '', '', '', ''))
        
        else:
            print(f"Row does not match pattern or is empty: {row}")

    return structured_data

def extract_tables_from_pages(pdf_path, bbox, page_numbers):
    """
    Extracts tables within the specified bounding box from specific pages of a PDF.
    
    Args:
        pdf_path (str): The path to the PDF file.
        bbox (tuple): A tuple specifying the bounding box (xmin, ymin, xmax, ymax).
        page_numbers (list of int): A list of page numbers from which to extract the tables (1-indexed).

    Returns:
        list: A list of tuples, where each tuple represents a row with five columns (Parameter, Currency1, Current year, Currency2, Previous year).
    """
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in page_numbers:
            if page_number < 1 or page_number > len(pdf.pages):
                raise ValueError(f"Page number {page_number} out of range")
            
            # Extract the specified page (convert to 0-indexed)
            page = pdf.pages[page_number - 1]
            
            # Extract text within the bounding box
            cropped_page = page.within_bbox(bbox)
            text = cropped_page.extract_text()
            if text:
                lines = text.split('\n')
                data.extend(lines)
    
    return extract_columns_regex(data)

def save_tables_to_csv(structured_data, filename):
    """
    Saves structured data to a CSV file.

    Args:
        structured_data (list): A list of tuples, where each tuple represents a row with five columns (Parame , Currency1, Current year, Currency2, Previous year).
        filename (str): The filename for the output CSV file.
    """
    df = pd.DataFrame(structured_data, columns=['Parameter', 'Currency1', 'Current year', 'Currency2', 'Previous year'])
    df.to_csv(filename, index=False)
    print(f"Saved table to {filename}")

    # Display the contents of the CSV file
    print("Contents of the CSV file:")
    print(df)
    return df

# Sample function to split extracted data into income statement and balance sheet tables
def split_into_tables(df):
    income_statement_table = []
    balance_sheet_table = []
    current_table = None  # To track which table (income statement or balance sheet)

    for index, row in df.iterrows():
        if is_income_statement_start(row['Parameter']):
            current_table = 'Income Statement'
        elif is_balance_sheet_start(row['Parameter']):
            current_table = 'Balance Sheet'

        if current_table == 'Income Statement':
            income_statement_table.append(row)
        elif current_table == 'Balance Sheet':
            balance_sheet_table.append(row)

    return income_statement_table, balance_sheet_table

# Example functions to check if a row indicates the start of Income Statement or Balance Sheet
def is_income_statement_start(parameter):
    keywords = ['Total Sales']
    for keyword in keywords:
        if keyword.lower() in parameter.lower():
            return True
    return False

def is_balance_sheet_start(parameter):
    keywords = ['Current Assets']
    for keyword in keywords:
        if keyword.lower() in parameter.lower():
            return True
    return False


# Example usage with your PDF file
pdf_path = "/Users/prakashsethu/Documents/Whole Balance sheets - updated - v2 (v1 errors removed)/Company 1 - Full Balance Sheet - Sheet1 with borders.pdf"

# Specify the page numbers (1-indexed)
page_numbers = [1,2,3,4,5,6]  # Example page numbers: for balance sheet and income statement

bbox = (163.5, 89.231325, 628.5, 539.99)  # Example values; adjust based on your document

# Extract tables from the PDF
structured_data = extract_tables_from_pages(pdf_path, bbox, page_numbers)



# Save extracted tables to CSV
DataFrame_Format = save_tables_to_csv(structured_data, "extracted_table.csv")

income_statement_table, balance_sheet_table = split_into_tables(DataFrame_Format)

    # Step 2: Print or further process the tables


income_statement_df = pd.DataFrame(income_statement_table)
balance_sheet_df = pd.DataFrame(balance_sheet_table)

# Print Income Statement Table as DataFrame
print("Income Statement Table:")
print(income_statement_df)

# Print Balance Sheet Table as DataFrame
print("\nBalance Sheet Table:")
print(balance_sheet_df)

# Extract text from the PDF
text = extract_text_from_pdf(pdf_path, page_numbers)
    
# Analyze the extracted text
company_name, quality_of_statements = analyze_text(text)
    
# Print or return the results
print("Company Name:", company_name)
print("Quality of Financial Statements:", quality_of_statements)


# Generate Financial Model
#____________________________________________________________________________________________________________________________
# Dictionary of metrics with possible names
metrics_to_extract = {
    'Revenue': ['Revenue', 'Total Income', 'Total Sales', 'Total Revenue'],
    'Cost of Goods Sold': ['Cost of Goods Sold', 'COGS','Cost of Sales'],
    'Gross Profit': ['Gross Profit', 'Gross Income'],
    'Net Income Before Taxes': ['Net Income Before Taxes', 'Earnings Before Tax', 'EBT','Income before taxes'],
    'Interest Expense': ['Interest Expense', 'Interest Cost','Interest on long term debt'],
    'Depreciation': ['Depreciation', 'Depreciation Expense', 'Amortization','Depreciation/ Amortization']
}

# Dictionary to store extracted metrics
extracted_metrics = {
    'Metric': [],
    'Current year': [],
    'Previous year': []
}

# Function to extract specific metric from dataframe
def extract_metric(df, metric_names):
    current_year_value = None
    previous_year_value = None
    
    for name in metric_names:
        for parameter in df['Parameter']:
            if name.lower() == parameter.lower():
                temp_current = df.loc[df['Parameter'] == parameter, 'Current year'].values[0]
                temp_previous = df.loc[df['Parameter'] == parameter, 'Previous year'].values[0]
                
                # Update if temp values are non-zero or if current value is None
                if temp_current is not None and temp_current != 0:
                    current_year_value = temp_current
                if temp_previous is not None and temp_previous != 0:
                    previous_year_value = temp_previous

    return current_year_value, previous_year_value

# Function to extract specific metrics from the income statement and balance sheet
def extract_metrics(income_statement_df, balance_sheet_df):
    metrics_to_extract = {
        'Revenue': ['Revenue', 'Total Income', 'Total Sales', 'Total Revenue'],
        'COGS': ['Cost of Goods Sold', 'COGS'],
        'Gross Profit': ['Gross Profit'],
        'NIBT': ['Net Income Before Taxes', 'Net Income', 'Net Profit Before Taxes'],
        'Interest Expense': ['Interest Expense', 'Interest Cost'],
        'Depreciation': ['Depreciation', 'Depreciation Expense']
    }
    
    extracted_data = {}
    
    for metric, names in metrics_to_extract.items():
        if metric in ['Revenue', 'COGS', 'Gross Profit', 'NIBT', 'Interest Expense', 'Depreciation']:
            current_year_value, previous_year_value = extract_metric(income_statement_df, names)
        else:
            current_year_value, previous_year_value = extract_metric(balance_sheet_df, names)
        
        extracted_data[metric] = {
            'Current Year': current_year_value,
            'Previous Year': previous_year_value
        }

    # Calculate EBITDA
    extracted_data['EBITDA'] = {
        'Current Year': (extracted_data['Gross Profit']['Current Year'] or 0) +
                        (extracted_data['Interest Expense']['Current Year'] or 0) +
                        (extracted_data['Depreciation']['Current Year'] or 0),
        'Previous Year': (extracted_data['Gross Profit']['Previous Year'] or 0) +
                         (extracted_data['Interest Expense']['Previous Year'] or 0) +
                         (extracted_data['Depreciation']['Previous Year'] or 0)
    }

    return extracted_data

# Example usage with dataframes
# Assume `income_statement_df` and `balance_sheet_df` are already created dataframes

extracted_data = extract_metrics(income_statement_df, balance_sheet_df)

# Convert the extracted data to a DataFrame for display
extracted_df = pd.DataFrame.from_dict(extracted_data, orient='index')
print(extracted_df)