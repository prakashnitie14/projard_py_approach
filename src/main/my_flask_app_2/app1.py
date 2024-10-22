import pandas as pd
import re

# Sample data: reading from CSV format directly for the sake of example.
data = """
Parameter,Currency1,Current year,Currency2,Previous year
notes to financial statements,,,,
year ended: dec,,31.0,,2023.0
nature of operations,,,,
abc28519909 xyz42563979 inc. is into frozen food manufacturing,,,,
1. significant accounting policies,,,,
these financial statements have been prepared in accordance with canadian accounting,,,,
standards for private enterprises. the significant accounting policies are detailed as follows:,,,,
cash,,,,
cash consists of balances with financial institutions,,,,
inventory,,,,
inventory is measured as lower of cost and net realizable value,,,,
"property, plant and equipment",,,,
property plant and equipment are recorded at cost. the company provides for amortization by,,,,
using the straight line method,,,,
2. cash and bank debt,,,,
jei bank has provided the company with committed revolving facility loan which bears a,,,,
floating interest at jei bank's prime rate,,,,
the revolving credit facility is secured by general security agreement issued by the company,,,,
"under the common control, representing a first charge on all present and after aquired",,,,
personal property. the total carrying amount of assets pledged as collateral under the gsa is,,,,
$,,104767.0,,6.0
3. inventory,,,,
31-dec-2023 31-dec,,-202.0,,2.0
finished goods,$,12157.0,$,2862.0
raw material,$,12057.0,$,3014.0
packaging and labels,$,4357.0,$,219.0
$,,28571.0,$,6096.0
"""
from io import StringIO
df = pd.read_csv(StringIO(data))

# Combine all columns into one text column (for simplification)
df['text'] = df.fillna('').apply(lambda row: ' '.join([str(x) for x in row if str(x).strip() != '']), axis=1)

# Segregation based on Note number, Schedule number, etc.
# Define patterns for splitting the notes (e.g., 1., 2., 3., Note 1, Schedule 1, etc.)
note_pattern = re.compile(r"^(?:\d+\.)|(?:Note \d+)|(?:Schedule \d+)", re.IGNORECASE)

# Initialize variables
notes = {}
current_note = None

# Iterate through each row and bucket them
for line in df['text']:
    # Check if the line starts a new note using the pattern
    if note_pattern.match(line):
        # Start a new note
        current_note = line.strip()  # Use the note number as the key
        notes[current_note] = []  # Initialize the note's content
    elif current_note:
        # Append lines to the current note's content
        notes[current_note].append(line.strip())

# Display the result (you can process or save it as variables as needed)
for note, content in notes.items():
    print(f"{note}:")
    print("\n".join(content))
    print("\n" + "="*50 + "\n")
