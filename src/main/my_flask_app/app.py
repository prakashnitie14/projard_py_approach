from flask import Flask, render_template, request, redirect, url_for
import os
import re
import pandas as pd
import pdfplumber
from flask_cors import CORS

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
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

def extract_tables_from_pages(pdf_path):
    """
    Extracts tables from all pages of a PDF.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        list: A list of tuples, where each tuple represents a row with columns (Parameter, Currency1, Current year, Currency2, Previous year).
    """
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text from the page
            text = page.extract_text()
            if text:
                # Split text into lines
                lines = text.split('\n')
                # Extend data with lines
                data.extend(lines)
    
    # Assuming extract_columns_regex is defined elsewhere and processes the lines into table rows
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
    cashflow_table = []
    notes_for_fs_table = []
    current_table = None  # To track which table (income statement or balance sheet)

    for index, row in df.iterrows():
        if is_income_statement_start(row['Parameter']):
            current_table = 'Income Statement'
        elif is_balance_sheet_start(row['Parameter']):
            current_table = 'Balance Sheet'
        elif is_cashflow_start(row['Parameter']):
            current_table = 'Cashflow Statement'
        elif is_notes_for_fs_start(row['Parameter']):
            current_table = 'Notes for Financial Statement'

        if current_table == 'Income Statement':
            income_statement_table.append(row)
        elif current_table == 'Balance Sheet':
            balance_sheet_table.append(row)
        elif current_table == 'Cashflow Statement':
            cashflow_table.append(row)
        elif notes_for_fs_table == 'Notes for Financial Statements':
            notes_for_fs_table.append(row)

    return income_statement_table, balance_sheet_table, cashflow_table, notes_for_fs_table

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

def is_cashflow_start(parameter):
    keywords = ['Statement of Cashflows']
    for keyword in keywords:
        if keyword.lower() in parameter.lower():
            return True
    return False

def is_notes_for_fs_start(parameter):
    keywords = ['Notes to Financial Statements']
    for keyword in keywords:
        if keyword.lower() in parameter.lower():
            return True
    return False

# Example usage with your PDF file
pdf_path = "/Users/prakashsethu/Documents/Whole Balance sheets - updated - v2 (v1 errors removed)/Company 1 - Full Balance Sheet - Sheet1-6.pdf"

# Extract tables from the PDF
structured_data = extract_tables_from_pages(pdf_path)

# Save extracted tables to CSV
DataFrame_Format = save_tables_to_csv(structured_data, "extracted_table.csv")

income_statement_table, balance_sheet_table, cashflow_table, notes_for_FS_table = split_into_tables(DataFrame_Format)

    # Step 2: Print or further process the tables

income_statement_df = pd.DataFrame(income_statement_table)
balance_sheet_df = pd.DataFrame(balance_sheet_table)
cashflow_df = pd.DataFrame(cashflow_table)

#cashflow_df = cashflow_df.drop(cashflow_df.index)

#cashflow_df = cashflow_df.drop(cashflow_df.columns, axis = 1)

# Print Income Statement Table as DataFrame
# print("Income Statement Table:")
# print(income_statement_df)

print ("Cashflow Table")
print (cashflow_df)

# Print Balance Sheet Table as DataFrame
print("\nBalance Sheet Table:")
print(balance_sheet_df)

# Extract text from the PDF
text = extract_text_from_pdf(pdf_path)
    
# Analyze the extracted text
company_name, quality_of_statements = analyze_text(text)
    
# Print or return the results
print("Company Name:", company_name)
print("Quality of Financial Statements:", quality_of_statements)


# Generate Financial Model

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

                # Convert to float, handling exceptions
                try:
                    temp_current = float(temp_current)
                except (TypeError, ValueError):
                    temp_current = None
                
                try:
                    temp_previous = float(temp_previous)
                except (TypeError, ValueError):
                    temp_previous = None

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
        'Depreciation': ['Depreciation', 'Depreciation Expense', 'Amortization', 'Depreciation/Amortization'],
        'One time gains (loss)': ['Gain from Sale of Assets','Gains through sale of property','Losses through sale of property','Gains (losses) through sale of property','Gains/ losses through sale of property','Gains/losses through sale of property','Loss through sale of property','Gains (loss) through sale of property','Gains/ loss through sale of property','Gains/loss through sale of property'],
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


def extract_dsc_table(income_statement_df, cashflow_df, extracted_data):

    # Extract Unfinanced Capex from Cashflow DataFrame
    capex_names = ["Purchase of new Property Plant and Equipment","Proceeds from sale of PP&E","Proceeds of long term debt"]
    unfinanced_capex_current_temp, unfinanced_capex_previous_temp = extract_metric(cashflow_df, capex_names, sum_values=True)

    unfinanced_capex_current = 0
    unfinanced_capex_previous = 0

    # Extract Distributions from Income Statement DataFrame
    distributions_names = ["Dividends Paid","Due to Shareholders","Due to Directors","Due to Related Parties","due from Related Parties","Due from Shareholders","Due from Directors"]
    distributions_current, distributions_previous = extract_metric(cashflow_df, distributions_names, sum_values=True)

    if distributions_current > 0:
        unfinanced_capex_current_temp = unfinanced_capex_current_temp + distributions_current
        distributions_current = 0
    
    if distributions_previous > 0:
        unfinanced_capex_previous_temp = unfinanced_capex_previous_temp + distributions_previous
        distributions_previous = 0

    if unfinanced_capex_current_temp > 0:
        unfinanced_capex_current = 0
    else:
        unfinanced_capex_current = unfinanced_capex_current_temp
        
    
    if unfinanced_capex_previous_temp > 0:
        unfinanced_capex_previous = 0
    else:
        unfinanced_capex_previous = unfinanced_capex_previous_temp

    # Extract Cash Taxes from Income Statement DataFrame
    cash_taxes_names = ["Income taxes"]
    cash_taxes_current, cash_taxes_previous = extract_metric(income_statement_df, cash_taxes_names, sum_values=True)

    # Extract more Cash Tax items from Cashflow Statement DataFrame
    cash_taxes_names1 = ["Income tax payable","Income tax receivable"]
    cash_taxes_current1, cash_taxes_previous1 = extract_metric(cashflow_df, cash_taxes_names1, sum_values=True)


    # Retrieve Adjusted EBITDA from extracted data
    adjusted_ebitda_current = extracted_data['Adjusted EBITDA']['Current Year']
    adjusted_ebitda_previous = extracted_data['Adjusted EBITDA']['Previous Year']

    # Retrieve Interest Cost from extracted data
    interest_expense_current = extracted_data['Interest Expense']['Current Year']
    interest_expense_previous = extracted_data['Interest Expense']['Previous Year']

    # Extract Repayment from Cashflow Statement DataFrame
    cash_taxes_names1 = ["Repayment of long term loan","Repayment of capital lease obligations"]
    repayment_amount_current, repayment_amount_previous = extract_metric(cashflow_df, cash_taxes_names1, sum_values=True)

    FCF_current = adjusted_ebitda_current + unfinanced_capex_current + distributions_current + (cash_taxes_current*-1)+cash_taxes_current1

    FCF_previous = adjusted_ebitda_previous + unfinanced_capex_previous + distributions_previous + (cash_taxes_previous*-1)+cash_taxes_previous1

    debt_service_cost_current = interest_expense_current + (repayment_amount_current*-1)
    debt_service_cost_previous = interest_expense_current + (repayment_amount_current*-1)

    # Create the DSC Table
    dsc_table = [
        {
            'Parameter': 'Adjusted EBITDA',
            'Current Year': adjusted_ebitda_current,
            'Previous Year': adjusted_ebitda_previous
        },
        {
            'Parameter': 'Unfinanced Capex',
            'Current Year': unfinanced_capex_current,
            'Previous Year': unfinanced_capex_previous
        },
        {
            'Parameter': 'Distributions',
            'Current Year': distributions_current,
            'Previous Year': distributions_previous
        },
        {
            'Parameter': 'Cash Taxes',
            'Current Year': (cash_taxes_current*-1)+cash_taxes_current1,
            'Previous Year': (cash_taxes_previous*-1)+cash_taxes_previous1
        },
        {
            'Parameter': 'Free Cashflow (FCF)',
            'Current Year': FCF_current,
            'Previous Year': FCF_previous
        },
        {
            'Parameter': 'Interest Expense',
            'Current Year': interest_expense_current,
            'Previous Year': interest_expense_previous
        },
        {
            'Parameter': 'Principal Repayment',
            'Current Year': repayment_amount_current*-1,
            'Previous Year': repayment_amount_previous*-1
        },
        {
            'Parameter': 'Debt Service Expense',
            'Current Year': debt_service_cost_current,
            'Previous Year': debt_service_cost_previous
        },
        {
            'Parameter': 'Debt Service Coverage (DSC)',
            'Current Year': FCF_current / (debt_service_cost_current),
            'Previous Year': FCF_previous / (debt_service_cost_previous)
        },
        {
            'Parameter': 'FCF Headroom',
            'Current Year': (FCF_current - debt_service_cost_current*1.1),
            'Previous Year': (FCF_previous - debt_service_cost_previous*1.1)
        }
    ]

    return pd.DataFrame(dsc_table)

def extract_dsc_table_from_balance_sheet(income_statement_df, balance_sheet_df, extracted_data):

    # Extract Unfinanced Capex from Cashflow DataFrame
    capex_names = ["Property and Equipment (Net of Accumulated Depreciation"]
    PPandE_current_temp, PPandE_previous_temp = extract_metric(balance_sheet_df, capex_names, sum_values=True)

    depreciation_current = extracted_data['Depreciation']['Current Year']
    depreciation_previous = extracted_data['Depreciation']['Previous Year']


    unfinanced_capex_current = 0
    unfinanced_capex_previous = 0

    unfinanced_capex_current = -PPandE_current_temp + (PPandE_previous_temp - depreciation_current)

    # Extract Distributions from Balance Sheet DataFrame
    distributions_names_liab = ["Due to Shareholders","Due to Directors","Due to Related Parties"]
    distributions_liab_current, distributions_liab_previous = extract_metric(balance_sheet_df, distributions_names_liab, sum_values=True)

    net_distributions_liab = distributions_liab_previous - distributions_liab_current

    distributions_names_assets = ["Due from Shareholders","Due from Directors","Due from Related Parties", "Loans to Related Parties"]
    distributions_asset_current, distributions_asset_previous = extract_metric(balance_sheet_df, distributions_names_assets, sum_values=True)

    net_distributions_asset = -distributions_asset_previous + distributions_asset_current

    # Extract dividend from Income Statement DataFrame
    dividends_names = ["Dividends paid","Dividends","Dividend"]
    dividends_current,dividends_prev = extract_metric(income_statement_df, dividends_names, sum_values=True)

    distributions_current = -net_distributions_asset - net_distributions_liab - dividends_current

    if unfinanced_capex_current > 0:
           unfinanced_capex_current = 0
    elif distributions_current > 0:
        unfinanced_capex_current  = unfinanced_capex_current + distributions_current

    # Extract Taxes from Income Statement DataFrame
    cash_taxes_names = ["Income taxes"]
    cash_taxes_PandL_current, cash_taxes_PandL_previous = extract_metric(income_statement_df, cash_taxes_names, sum_values=True)

    # Extract more Cash Tax items from Balance Sheet (Asset) DataFrame
    cash_taxes_names_asset = ["Income tax receivable","Income tax recoverable"]
    cash_taxes_asset_current, cash_taxes_asset_prev = extract_metric(balance_sheet_df, cash_taxes_names_asset, sum_values=True)

    net_cashtax_asset = cash_taxes_asset_current - cash_taxes_asset_prev
    
    # Extract more Cash Tax items from Balance Sheet (Liabilities) DataFrame
    cash_taxes_names_liab = ["Income tax Payable","Tax payable","Income taxes Payable","Taxes payable"]
    cash_taxes_liab_current, cash_taxes_liab_prev = extract_metric(balance_sheet_df, cash_taxes_names_liab, sum_values=True)

    net_cashtax_liab = - cash_taxes_liab_current + cash_taxes_liab_prev

    net_cash_tax = -cash_taxes_PandL_current - net_cashtax_asset - net_cashtax_liab

    if net_cash_tax > 0:
        net_cash_tax = 0
    
    # Retrieve Adjusted EBITDA from extracted data
    adjusted_ebitda_current = extracted_data['Adjusted EBITDA']['Current Year']
    adjusted_ebitda_previous = extracted_data['Adjusted EBITDA']['Previous Year']

    # Retrieve Interest Cost from extracted data
    interest_expense_current = extracted_data['Interest Expense']['Current Year']
    interest_expense_previous = extracted_data['Interest Expense']['Previous Year']

    # Extract Repayment from Cashflow Statement DataFrame
    Longterm_debt_names = ["Long Term Debt","Obligations under Capital Lease","Capital Lease","Term Debt","Current portion of long term debt","Current portion of obligations under capital lease"]
    Longterm_debt_current, Longterm_debt_previous = extract_metric(balance_sheet_df, Longterm_debt_names, sum_values=True)

    print (Longterm_debt_current, Longterm_debt_previous)

    # Extract CPLTD from Balancesheet DataFrame
    Longterm_debt_names = ["Current portion of long term debt","Current portion of obligations under capital lease"]
    cpltd_debt_current, cpltd_debt_previous = extract_metric(cashflow_df, Longterm_debt_names, sum_values=True)


    repayment_amount_current = Longterm_debt_previous - Longterm_debt_current

    if repayment_amount_current < 0:
        unfinanced_capex_current = unfinanced_capex_current + (repayment_amount_current*-1)
        repayment_amount_current = 0

    if unfinanced_capex_current > 0:
           unfinanced_capex_current = 0 
    
    repayment_amount_previous = cpltd_debt_previous



    FCF_current = adjusted_ebitda_current + unfinanced_capex_current + distributions_current + net_cash_tax

    FCF_previous = adjusted_ebitda_previous + unfinanced_capex_previous

    debt_service_cost_current = interest_expense_current + repayment_amount_current
    debt_service_cost_previous = interest_expense_previous + repayment_amount_previous

    # Create the DSC Table
    dsc_table = [
        {
            'Parameter': 'Adjusted EBITDA',
            'Current Year': adjusted_ebitda_current,
            'Previous Year': adjusted_ebitda_previous
        },
        {
            'Parameter': 'Unfinanced Capex',
            'Current Year': unfinanced_capex_current,
            'Previous Year': unfinanced_capex_previous
        },
        {
            'Parameter': 'Distributions',
            'Current Year': distributions_current,
            'Previous Year': 0
        },
        {
            'Parameter': 'Cash Taxes',
            'Current Year': net_cash_tax,
            'Previous Year': 0
        },
        {
            'Parameter': 'Free Cashflow (FCF)',
            'Current Year': FCF_current,
            'Previous Year': FCF_previous
        },
        {
            'Parameter': 'Interest Expense',
            'Current Year': interest_expense_current,
            'Previous Year': interest_expense_previous
        },
        {
            'Parameter': 'Principal Repayment',
            'Current Year': repayment_amount_current,
            'Previous Year': repayment_amount_previous
        },
        {
            'Parameter': 'Debt Service Expense',
            'Current Year': debt_service_cost_current,
            'Previous Year': debt_service_cost_previous
        },
        {
            'Parameter': 'Debt Service Coverage (DSC)',
            'Current Year': FCF_current / (debt_service_cost_current),
            'Previous Year': FCF_previous / (debt_service_cost_previous)
        },
        {
            'Parameter': 'FCF Headroom',
            'Current Year': (FCF_current - debt_service_cost_current*1.1),
            'Previous Year': (FCF_previous - debt_service_cost_previous*1.1)
        }
    ]

    return pd.DataFrame(dsc_table)
# Example usage with extracted dataframes and metrics

if cashflow_df.empty:
 dsc_df = extract_dsc_table_from_balance_sheet(income_statement_df, balance_sheet_df, extracted_data)
 print ('DSC using balance sheet approach')
else:
 
 dsc_df = extract_dsc_table(income_statement_df, cashflow_df, extracted_data)
 print ('DSC using cashflow statement approach')
 

# Convert the extracted data to a DataFrame for display
extracted_df = pd.DataFrame.from_dict(extracted_data, orient='index')
print ('This is operating financial statements')
print(extracted_df)

print ('Debt service coverage table')
print(dsc_df)

def calculate_roe(income_statement_df, balance_sheet_df):
    """
    Calculate Return on Equity (ROE) using income statement and balance sheet data frames.

    Args:
        income_statement_df (DataFrame): The DataFrame containing the income statement data.
        balance_sheet_df (DataFrame): The DataFrame containing the balance sheet data.

    Returns:
        float: The Return on Equity (ROE) value.
    """
    # Define the metric names for net income and shareholders' equity
    net_income_names = ["Net Income", "Net Profit", "Net Earnings"]
    equity_names = ["Share Equity", "Preference Shares", "Retained earnings", "Paid up capital", "Share Capital"]

    # Extract net income and equity values using the extract_value function
    net_income_current, net_income_previous = extract_metric(income_statement_df, net_income_names)
    total_equity_current, total_equity_previous = extract_metric(balance_sheet_df, equity_names, sum_values= True)

    # Check if the necessary values are retrieved
    if net_income_current is None:
        raise ValueError("Net income not found in the income statement for current year.")
    if total_equity_current is None:
        raise ValueError("Shareholders' equity not found in the balance sheet for current year.")

    # Calculate ROE
    roe_current_current = net_income_current / total_equity_current
    roe_current_previous = net_income_previous / total_equity_previous

    # Create ROE table
    roe_table = pd.DataFrame({
        'Parameter': ['Return on Equity (ROE)'],
        'Current Year': [roe_current_current],
        'Previous Year': [roe_current_previous]
    })

    return roe_table

# Assuming income_statement_df and balance_sheet_df are already defined

roe_table = calculate_roe(income_statement_df, balance_sheet_df)
print("Return on Equity (ROE):")

print (roe_table)

def extract_book_leverage_ratio(balance_sheet_df):
    # Define the metric names for each row
    total_equity_names = ["Total Equity","Equity","Total Shareholders Equity"]
    equity_names = ["Share Capital", "Preference Shares", "Retained Earnings"]
    loans_from_related_names = ["Loans from Shareholders", "Loans from Related Parties", "Due to Shareholders", 
                                "Due to Directors", "Due to Related Parties", "Loans from Directors"]
    loans_to_related_names = ["Loans to Shareholders", "Loans to Related Parties", "Due from Shareholders", "Due from Directors", 
                              "Due from Related Parties", "Loans to Related Directors"]
    related_party_investments = ["Investments in related party","Investments in related companies"]
    goodwill_intangible_names = ["Goodwill", "Intangible Assets", "Intangible Asset"]
    total_liabilities_names = ["Total Liabilities"]
    total_liabilities_2parts_names = ["Total Current Liabilities","Total Non Current Liabilities","Total Non-Current Liabilities"]
    liability_componant_names =  ["Bank Indebtedness", "Short term debt","Accounts Payable", "Supplier accounts",
                                  "Accounts Payable and Accrued Liabilities","Income tax payable","Customer Deposits",
                                  "Deposits Received","CPLTD","Current portion of long term debt",
                                  "Current portion of obligations under capital lease","Government Remottances",
                                  "Government Remittances Payable","Deferred income","Government loan","Long Term debt",
                                  "Term loan","non current debt","non-current debt",
                                  "Obligations under Capital Lease","Due to Shareholders","Due to Directors",
                                  "Due to Related Parties","Loan from Shareholders","Loan from Directors",
                                  "Loan from Related Parties"]
    
    # Extract the metrics using the extract_metric function
    equity_base_current, equity_base_previous = extract_metric(balance_sheet_df, total_equity_names)
    
    if equity_base_current is None:
       equity_base_current, equity_base_previous = extract_metric(balance_sheet_df, equity_names, sum_values= True)
    
    loans_from_related_current, loans_from_related_previous = extract_metric(balance_sheet_df, loans_from_related_names, sum_values=True)
    loans_to_related_current, loans_to_related_previous = extract_metric(balance_sheet_df, loans_to_related_names, sum_values=True)
    related_party_inv_current, related_party_inv_previous = extract_metric(balance_sheet_df, related_party_investments, sum_values=True)
    goodwill_intangible_current, goodwill_intangible_previous = extract_metric(balance_sheet_df, goodwill_intangible_names, sum_values=True)
    total_liabilities_current, total_liabilities_previous = extract_metric(balance_sheet_df, total_liabilities_names)

    if total_liabilities_current is None:
        total_liabilities_current, total_liabilities_previous = extract_metric(balance_sheet_df, total_liabilities_2parts_names)

    if total_liabilities_current is None:
        total_liabilities_current, total_liabilities_previous = extract_metric(balance_sheet_df, liability_componant_names, sum_values= True)
    
    # Calculate Tangible Net Worth (TNW)
    tnw_current = (equity_base_current + loans_from_related_current - loans_to_related_current - related_party_inv_current - goodwill_intangible_current)
    tnw_previous = (equity_base_previous + loans_from_related_previous - loans_to_related_previous - related_party_inv_previous - goodwill_intangible_previous)
    
    # Calculate Net Liabilities
    net_liabilities_current = total_liabilities_current - loans_from_related_current
    net_liabilities_previous = total_liabilities_previous - loans_from_related_previous
    
    # Calculate Debt/TNW ratio
    debt_tnw_current = net_liabilities_current / tnw_current if tnw_current != 0 else None
    debt_tnw_previous = net_liabilities_previous / tnw_previous if tnw_previous != 0 else None
    
    #Define Book Leverage Threshold
    book_lev_threshold = 3

    #Calculate Book Leverage Headroom
    if debt_tnw_current < book_lev_threshold and debt_tnw_current > 0:
        debt_headroom_current = tnw_current*book_lev_threshold - net_liabilities_current
    else:
        debt_headroom_current = "NA"

    if debt_tnw_previous < book_lev_threshold and debt_tnw_previous > 0:
        debt_headroom_previous = tnw_previous*book_lev_threshold - net_liabilities_previous
    else:
        debt_headroom_previous = "NA"

    # Create the Book Leverage Ratio Table
    book_leverage_ratio_table = [
        {
            'Parameter': 'Equity Base',
            'Current Year': equity_base_current,
            'Previous Year': equity_base_previous
        },
        {
            'Parameter': 'Add: Loans from Related Parties',
            'Current Year': loans_from_related_current,
            'Previous Year': loans_from_related_previous
        },
        {
            'Parameter': 'Deduct: Loans to Related Parties',
            'Current Year': loans_to_related_current,
            'Previous Year': loans_to_related_previous
        },
        {
            'Parameter': 'Deduct: Goodwill/Intangible Assets',
            'Current Year': goodwill_intangible_current,
            'Previous Year': goodwill_intangible_previous
        },
        {
            'Parameter': 'Tangible Net Worth (TNW)',
            'Current Year': tnw_current,
            'Previous Year': tnw_previous
        },
        {
            'Parameter': 'Total Liabilities',
            'Current Year': total_liabilities_current,
            'Previous Year': total_liabilities_previous
        },
        {
            'Parameter': 'Deduct: Loans from Related Parties',
            'Current Year': loans_from_related_current,
            'Previous Year': loans_from_related_previous
        },
        {
            'Parameter': 'Net Liabilities',
            'Current Year': net_liabilities_current,
            'Previous Year': net_liabilities_previous
        },
        {
            'Parameter': 'Debt/TNW',
            'Current Year': debt_tnw_current,
            'Previous Year': debt_tnw_previous
        },
        {
            'Parameter': 'Book Leverage Threshold',
            'Current Year': book_lev_threshold,
            'Previous Year': book_lev_threshold
        },
        {
            'Parameter': 'Book Leverage Headroom',
            'Current Year': debt_headroom_current,
            'Previous Year': debt_headroom_previous
        }
    ]
    
    return pd.DataFrame(book_leverage_ratio_table)


# Example usage
book_leverage_ratio_df = extract_book_leverage_ratio(balance_sheet_df)

print ("Book Leverage Calculation")
print(book_leverage_ratio_df)


app = Flask(__name__)

# Set up the upload folder in Flask's config
app.config['UPLOAD_FOLDER'] = 'uploads'

# Enable CORS for the app
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Adjust origin as needed

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/balance-sheet', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            extracted_data1 = extract_data_from_pdf(
                          income_statement_df, 
                          balance_sheet_df, 
                          cashflow_df, 
                          extracted_df, 
                          dsc_df, 
                          roe_table, 
                          book_leverage_ratio_df)
            return render_template('results.html', **extracted_data1)
    return render_template('upload.html')

def extract_data_from_pdf(
                          income_statement_df, 
                          balance_sheet_df, 
                          cashflow_df, 
                          extracted_data, 
                          dsc_df, 
                          roe_table, 
                          book_leverage_ratio_df):
    extracted_data1 = {
        "income_statement": income_statement_df,
        "balance_sheet": balance_sheet_df,
        "cashflow_statement": cashflow_df,
        "operating_financials": extracted_data,
        "dsc_table": dsc_df,
        "roe_table": roe_table,
        "book_leverage_table": book_leverage_ratio_df
    }
    return extracted_data1

if __name__ == '__main__':
    app.run(debug=True)