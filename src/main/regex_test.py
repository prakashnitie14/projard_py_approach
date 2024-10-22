import re

# Example pattern
pattern_right_to_left = re.compile(
    r'(.+?)\s*([\$€£¥₹]?)\s*(-?\(?[\d,]+(?:\.\d{1,2})?\)?)\s*([\$€£¥₹]?)\s*(-?\(?[\d,]+(?:\.\d{1,2})?\)?)$'
)

# Test lines
lines = [
    "Revenue Growth (note 12) 12,345 14,567",
    "Net Profit Increase $9,876 $10,234",
    "Total Assets 12345 14000"
]

# Structured data storage
structured_data = []

for line in lines:
    match = pattern_right_to_left.match(line)
    if match:
        column1, col2_currency, column2, col3_currency, column3 = match.groups()
        structured_data.append({
            "Column 1": column1.strip(),
            "Column 2": f"{col2_currency}{column2}",
            "Column 3": f"{col3_currency}{column3}"
        })

# Display results
for data in structured_data:
    print(data)

r'(.+?)\s*([\$€£¥₹]?)\s*(-?\$?\(?[\d,]+(?:\.\d{1,2})?\)?)\s*([\$€£¥₹]?)\s*(-?\$?\(?[\d,]+(?:\.\d{1,2})?\)?)'
r'(.+?)\s*([\$€£¥₹]?)\s*(-?\(?[\d,]+(?:\.\d{1,2})?\)?)\s*([\$€£¥₹]?)\s*(-?\(?[\d,]+(?:\.\d{1,2})?\)?)$'wsdrfgv l,oi99ikl;.