import re
import pandas as pd

# Sample input data (replace with your actual text)
input_text = """
Combined Statement of Balance Sheets
ABC19210180 XYZ69353790 Inc. 31-Dec-2023 31-Dec-2022
Current Assets
Cash and Cash Equivalents
Term Deposits
Accounts Receivable
Inventory
Harminized Sales Tax Receivable
Prepaid Expenses
Deposits
Marketable Securities
Investments
Income tax receivable
Restricted Cash
Interest Receivable
Mortgage Receivable
Dividends Receivable from join venture investments Loans from related parties
Non Current Assets
Property and Equipment (Net of Accumulated Depreciation) Due from Related Parties
Due from Shareholders
Due from Directors
Deposits
Investments
Cash surrender value of Life Insurance
Goodwill
Intangible assets
$4,000 $84,846 $43,983 $24,423 $55,575 $74,049 $20,031 $53,897 $72,611 $64,211 $26,323 $14,363
$2,138 $67,300 $94,883 $88,245 $99,028 $71,542 $11,161 $48,209 $57,761 $61,525
$3,386 $69,311 $22,954 $88,583 $74,071 $46,000 $15,133 $40,751
$603,038 $897,255
$78,572 $13,319 $19,688 $72,438 $39,978 $81,557 $88,491 $76,794 $62,613 $41,482 $21,205 $19,867 $86,442 $80,790 $37,895 $91,881
$1,925 $50,681 $436,809 $528,809
"""

def parse_text_to_dataframe(text):
    lines = text.strip().split("\n")
    data = []

    for line in lines:
        # Check if the line contains monetary values
        if re.match(r'^\$[\d,.]+$', line.strip()):
            values = line.strip().split()
            data[-1].extend(values)  # Extend the previous row with values
        else:
            data.append([line.strip(), "", "", "", ""])  # Create a new row

    # Create DataFrame
    df = pd.DataFrame(data, columns=['Parameter', 'Currency1', 'Current year', 'Currency2', 'Previous year'])
    return df

# Parse the input text into a DataFrame
df = parse_text_to_dataframe(input_text)
print(df)
