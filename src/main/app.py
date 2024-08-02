from flask import Flask, request, render_template, redirect, url_for
import os
import pdfplumber

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_data.append(page.extract_text())
    return "\n".join(text_data)

def process_pdf(file_path):
    extracted_text = extract_text_from_pdf(file_path)
    # Placeholder for data extraction logic
    income_statement = "Income Statement data"
    balance_sheet = "Balance Sheet data"
    cashflow_statement = "Cashflow Statement data"
    operating_financials = "Operating Financials data"
    dsc_table = "DSC Table data"
    roe_table = "Return on Equity Table data"
    leverage_table = "Book Leverage Table data"
    
    return {
        "income_statement": income_statement,
        "balance_sheet": balance_sheet,
        "cashflow_statement": cashflow_statement,
        "operating_financials": operating_financials,
        "dsc_table": dsc_table,
        "roe_table": roe_table,
        "leverage_table": leverage_table
    }

@app.route('/')
def index():
    app.logger.debug('Rendering index.html')
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.debug('No file part in request.files')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        app.logger.debug('No selected file')
        return redirect(request.url)
    
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        app.logger.debug(f'Saving file to {file_path}')
        file.save(file_path)
        data = process_pdf(file_path)
        app.logger.debug(f'Render results.html with data: {data}')
        return render_template('results.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)