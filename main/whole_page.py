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

# Clean up the structured data
def clean_parameter(param):
    # Remove special characters, numbers, and certain words
    param = re.sub(r'[()\[\]{}#@!$%^&*]', '', param)  # Remove special characters
    param = re.sub(r'\d+', '', param)  # Remove numbers
    param = re.sub(r'\b(Note|note)\b', '', param)  # Remove the word "Note"
    return param.strip()

def extract_tables_from_pages(pdf_path, page_numbers):
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
            
            text = page.extract_text()
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
    keywords = ['Total Sales', 'Sales','Income','Operating revenues']
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
pdf_path = "/Users/prakashsethu/Documents/Whole Balance sheets - updated - v2 (v1 errors removed)/2024_Q1_Financial_Statements_MDA_Final.pdf"

# Specify the page numbers (1-indexed)
page_numbers = [1,2]  # Example page numbers: for balance sheet and income statement

#bbox = (0.0, 0.0, 612.0, 79)   # Example values; adjust based on your document

# Extract tables from the PDF
structured_data = extract_tables_from_pages(pdf_path, page_numbers)

cleaned_data = [(clean_parameter(param), cur1, cur_val, cur2, prev_val) for param, cur1, cur_val, cur2, prev_val in structured_data]


# Save extracted tables to CSV
DataFrame_Format = save_tables_to_csv(cleaned_data, "extracted_table.csv")

income_statement_table, balance_sheet_table = split_into_tables(DataFrame_Format)

    # Step 2: Print or further process the tables


income_statement_df = pd.DataFrame(income_statement_table)
balance_sheet_df = pd.DataFrame(balance_sheet_table)

# Print Income Statement Table as DataFrame
print("Income Statement Table:")
print(income_statement_df)

# Print Balance Sheet Table as DataFrame
#print("\nBalance Sheet Table:")
#print(balance_sheet_df)

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

# Dictionary to store extracted metrics
extracted_metrics = {
    'Metric': [],
    'Current year': [],
    'Previous year': []
}

# Function to extract specific metrics from the income statement and balance sheet
def extract_metric(df, metric_names, sum_values=False):
    current_year_value = 0 if sum_values else None
    previous_year_value = 0 if sum_values else None
    current_year_found = False
    previous_year_found = False

    for name in metric_names:
        for index, row in df.iterrows():
            if name.lower() == row['Parameter'].lower():
                temp_current = row['Current year']
                temp_previous = row['Previous year']

                if sum_values:
                    if temp_current is not None and temp_current != 0:
                        current_year_value += temp_current
                        current_year_found = True
                    if temp_previous is not None and temp_previous != 0:
                        previous_year_value += temp_previous
                        previous_year_found = True
                else:
                    if temp_current is not None and temp_current != 0 and temp_current != '' and current_year_value is None:
                        current_year_value = temp_current
                        current_year_found = True
                    if temp_previous is not None and temp_previous != 0 and temp_previous != '' and previous_year_value is None:
                        previous_year_value = temp_previous
                        previous_year_found = True
                    if current_year_found and previous_year_found:
                        break

    if not sum_values:
        current_year_value = current_year_value if current_year_found else None
        previous_year_value = previous_year_value if previous_year_found else None

    return current_year_value, previous_year_value

# Function to extract specific metrics from the income statement and balance sheet
def extract_metrics(income_statement_df, balance_sheet_df):
    metrics_to_extract = {
        'Revenue': ['Revenue', 'Income', 'Total Sales', 'Total Income','Sales','Total operating revenues'],
        'COGS': ['Cost of Goods Sold', 'COGS', 'Cost of Sales'],
        'Gross Profit': ['Gross Profit', 'Gross Margins'],
        'NIBT': ['Net Income Before Taxes', 'Income before taxes', 'Net Profit Before Taxes','Earnings before income taxes'],
        'Interest Expense': ['Interest Expense', 'Interest Cost', 'Interest and Bank charges','Interest on long term debt'],
        'Depreciation': ['Depreciation', 'Depreciation Expense', 'Amortization', 'Depreciation/Amortization','Depreciation and amortization'],
        'One time gains (loss)': ['Gain from Sale of Assets','Gains through sale of property','Losses through sale of property','Gains (losses) through sale of property','Gains/ losses through sale of property','Gains/losses through sale of property','Loss through sale of property','Gains (loss) through sale of property','Gains/ loss through sale of property','Gains/loss through sale of property','Income from equity investments'],
        'FX Gains/ (loss)': ['FX Gains', 'FX Losses', 'FX Gains/Losses','FX Loss', 'FX Gains/Loss','Foreign exchange gains (losses)',
                             'Loss (gain) on foreign exchange'],
        'Govt Grant': ['Government Grant', 'Government Grants', 'CEWS','Govt Grant']
    }
    
    extracted_data = {}
    
    def try_convert_to_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    for metric, names in metrics_to_extract.items():
        if metric in ['Revenue', 'COGS', 'Gross Profit', 'NIBT', 'Depreciation','One time gains (loss)','Govt Grant']:
            current_year_value, previous_year_value = extract_metric(income_statement_df, names)
        elif metric == 'Interest Expense':
            current_year_value, previous_year_value = extract_metric(income_statement_df, names, sum_values=True)
        elif metric == 'FX Gains/ (loss)':
            current_year_value, previous_year_value = extract_metric(income_statement_df, names, sum_values=True)
        else:
            current_year_value, previous_year_value = extract_metric(balance_sheet_df, names)
        
        # Convert to float
        current_year_value = try_convert_to_float(current_year_value)
        previous_year_value = try_convert_to_float(previous_year_value)

        extracted_data[metric] = {
            'Current Year': current_year_value,
            'Previous Year': previous_year_value
        }
    
    # Compute Revenue Growth YoY
    revenue_current = extracted_data['Revenue']['Current Year']
    revenue_previous = extracted_data['Revenue']['Previous Year']
    if revenue_current is not None and revenue_previous is not None and revenue_previous != 0:
        revenue_growth_yoy = ((revenue_current - revenue_previous) / revenue_previous) * 100
    else:
        revenue_growth_yoy = None
    
    extracted_data['Revenue Growth YoY'] = {
        'Current Year': revenue_growth_yoy,
        'Previous Year': None
    }
    
    # Compute Gross Profit Margin
    gross_profit_current = extracted_data['Gross Profit']['Current Year']
    gross_profit_previous = extracted_data['Gross Profit']['Previous Year']
    if gross_profit_current is not None and revenue_current is not None and revenue_current != 0:
        gross_profit_margin_current = (gross_profit_current / revenue_current) * 100
    else:
        gross_profit_margin_current = None
    
    if gross_profit_previous is not None and revenue_previous is not None and revenue_previous != 0:
        gross_profit_margin_previous = (gross_profit_previous / revenue_previous) * 100
    else:
        gross_profit_margin_previous = None
    
    extracted_data['Gross Profit Margin'] = {
        'Current Year': gross_profit_margin_current,
        'Previous Year': gross_profit_margin_previous
    }
    
    # Compute EBITDA
    if all(key in extracted_data for key in ['NIBT', 'Interest Expense', 'Depreciation']):
        ebitda_current = sum([try_convert_to_float(extracted_data[key]['Current Year']) for key in ['NIBT', 'Interest Expense', 'Depreciation'] if extracted_data[key]['Current Year'] is not None])
        ebitda_previous = sum([try_convert_to_float(extracted_data[key]['Previous Year']) for key in ['NIBT', 'Interest Expense', 'Depreciation'] if extracted_data[key]['Previous Year'] is not None])
    else:
        ebitda_current = None
        ebitda_previous = None

    extracted_data['EBITDA'] = {
        'Current Year': ebitda_current,
        'Previous Year': ebitda_previous
    }
    
    # Compute Adjusted EBITDA
    def get_value(metric, period):
        value = extracted_data.get(metric, {}).get(period, 0)
        return try_convert_to_float(value) if value is not None else 0
    
    print (extracted_data)

    ebitda_current = get_value('EBITDA', 'Current Year')
    ebitda_previous = get_value('EBITDA', 'Previous Year')

    
    one_time_gains_current = get_value('One time gains (loss)', 'Current Year')
    one_time_gains_previous = get_value('One time gains (loss)', 'Previous Year')

    fx_gains_current = get_value('FX Gains/ (loss)', 'Current Year')
    fx_gains_previous = get_value('FX Gains/ (loss)', 'Previous Year')
    
    gov_grant_current = get_value('Govt Grant', 'Current Year')
    gov_grant_previous = get_value('Govt Grant', 'Previous Year')
    
    adjusted_ebitda_current = ebitda_current - one_time_gains_current - fx_gains_current - gov_grant_current
    adjusted_ebitda_previous = ebitda_previous - one_time_gains_previous - fx_gains_previous - gov_grant_previous
    
    extracted_data['Adjusted EBITDA'] = {
        'Current Year': adjusted_ebitda_current,
        'Previous Year': adjusted_ebitda_previous
    }

    return extracted_data

# Example usage with dataframes
# Assume `income_statement_df` and `balance_sheet_df` are already created dataframes

extracted_data = extract_metrics(income_statement_df, balance_sheet_df)

# Convert the extracted data to a DataFrame for display
extracted_df = pd.DataFrame.from_dict(extracted_data, orient='index')
print(extracted_df)