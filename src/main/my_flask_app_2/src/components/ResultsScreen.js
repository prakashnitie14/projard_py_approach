import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Navbar, Nav } from 'react-bootstrap';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import './Table.css';

const ResultsScreen = () => {
  const [responseData, setResponseData] = useState(null);
  const [fileURL, setfileURL] = useState(null);
  const [selectedOption, setSelectedOption] = React.useState('Income Statement');
  const [selectedNote, setSelectedNote] = React.useState(null);  // For storing the selected note
  const navigate = useNavigate();
  const location = useLocation();

  // Debugging: Check if data is received correctly
  console.log('File URL:', fileURL);
  console.log('Response Data:', responseData);

  useEffect(() => {
    const tableContainer = document.querySelector('.html-content-container');

    if (tableContainer) {
      tableContainer.addEventListener('click', (event) => handleNoteClick(event));
    }

    if (location.state?.responseData) {
      setResponseData(location.state.responseData);
      setfileURL(location.state.fileURL);
      localStorage.setItem('responseData', JSON.stringify(location.state.responseData)); // Save to localStorage
      localStorage.setItem('fileURL', JSON.stringify(location.state.fileURL));
    } else {
      const savedData = localStorage.getItem('responseData');  // Retrieve from localStorage if available
      const savedURL = localStorage.getItem('fileURL');  // Retrieve from localStorage if available
      if (savedData) {
        setResponseData(JSON.parse(savedData));
        setfileURL(JSON.parse(savedURL));
      } else {
        navigate('/upload');
      }
    }
  }, [location.state, navigate]);

  const handleNoteClick = (event) => {
    console.log('Note clicked');
    event.preventDefault();
    const noteLinkText = event.target.innerText;
    console.log('Selected link text :', noteLinkText);
    const noteContent = responseData.notes[noteLinkText];
    setSelectedNote(noteContent);
  };
  // utility.js

  const applyColorCoding = (htmlString) => {
    // Use a DOMParser to parse and manipulate the HTML string
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');

    // Find all table rows
    const rows = doc.querySelectorAll('tr');
    // Handle note clicks

    // Loop through rows to find "Growth/Fall" column and apply color to column "C"
    rows.forEach((row, index) => {
      if (index > 0) { // Skip the header row
        const growthFallCol = row.cells[5];
        const colC = row.cells[6];

        const notesCol = row.cells[2];  // Assuming "Notes" is in column 4 (index 1)

        // If the "Notes" column contains references like "(note 2)"
        if (notesCol && notesCol.innerText.trim()) {  // If the Notes column has content
          const noteContent = notesCol.innerText.trim();
          notesCol.innerHTML = `<a href="#" class="note-link">${noteContent}</a>`;
          const noteLink = notesCol.querySelector('.note-link');
        }

        // Extract and clean the "Growth/Fall" value (assuming it contains a %)
        const growthFallValue = parseFloat(growthFallCol.innerText.replace('%', '').replace('growth', '').replace('fall', '').trim());

        // If "Growth/Fall" is greater than 10%, color column "C" in red
        if (growthFallValue > 10) {
          colC.style.backgroundColor = 'red'; // Change the background color
        } else {
          colC.style.backgroundColor = ''; // Reset background color if not greater than 10%
        }
      }
    });

    // Return the modified HTML string
    return doc.body.innerHTML;
  }

  const defaultLayoutPluginInstance = defaultLayoutPlugin();


  const getHtmlContent = () => {
    if (!responseData || !responseData.income_statement) return '<p>No data available</p>';
    switch (selectedOption) {
      case 'Income Statement':
        return applyColorCoding(responseData.income_statement) || '<p>No Data available</p>';
      // case 'Balance Sheet':
      //   return applyColorCoding(responseData.balance_sheet) || '<p>No Data available</p>'
      // case 'Cashflow Statement (if available)':
      //   return applyColorCoding(responseData.balance_sheet) || '<p>No data available</p>';
      // case 'Operating Financial Metrics':
      //   return responseData.operating_financials || '<p>No data available</p>';
      // case 'Debt Service Coverage (DSC)':
      //   return responseData.dsc_table || '<p>No data available</p>';
      // case 'Book Leverage - Debt/ TNW':
      //   return responseData.book_leverage_table || '<p>No data available</p>';
      // case 'Return on Equity (ROE)':
      //   return responseData.roe_table || '<p>No data available</p>';
      // case 'Cashflow Leverage (Debt / EBITDA)':
      //   return responseData.cashflow_leverage_table || '<p>No data available</p>';
      // case 'Notes to financial statement':
      //   return responseData.notes_dict || '<p>No data available</p>';
      default:
        return '<p>No data available</p>';
    }
  };

  // If no fileURL or responseData, prevent rendering
  if (!responseData) {
    return <div>Loading...</div>; // Add a loading state or navigate back to upload
  }

  return (
    <div style={{ flex: '1', display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Navbar */}
      <Navbar bg="light" expand="lg">
        <Navbar.Brand href="/">TARS V1</Navbar.Brand>
        <Nav className="ml-auto">
          {/* Other Nav items if needed */}
        </Nav>
      </Navbar>

      <div style={{ display: 'flex', flex: 1 }}>
        {/* Left Segment */}
        <div style={{ flex: 1, padding: '20px', borderRight: '1px solid #ccc' }}>
          <h2>Copy of the Uploaded Financial Statement</h2>
          {/* Display PDF */}
          {fileURL && (
            <div>
              <Worker workerUrl={`https://unpkg.com/pdfjs-dist@3.0.279/build/pdf.worker.min.js`}>
                <div style={{ height: '750px', width: '100%' }}>
                  <Viewer fileUrl={fileURL} plugins={[defaultLayoutPluginInstance]} />
                </div>
              </Worker>
            </div>
          )}
        </div>

        {/* Right Segment */}
        <div style={{ flex: 1, padding: '20px', display: 'flex', flexDirection: 'column' }}>
          <div>
            <div>
              <strong>Company Name:</strong>
              <div>{responseData.companyName || 'N/A'}</div>
            </div>
            <div>
              <strong>Financial Statement Quality:</strong>
              <div>{responseData.financialStatementQuality || 'N/A'}</div>
            </div>
          </div>
          <select
            onChange={(e) => {
              setSelectedOption(e.target.value);
            }}
            value={selectedOption}
            style={{ marginTop: '20px' }}
          >
            <option value="Income Statement">Income Statement</option>
            <option value="Balance Sheet">Balance Sheet</option>
            <option value="Cashflow Statement (if available)">Cashflow Statement (if available)</option>
            <option value="Operating Financial Metrics">Operating Financial Metrics</option>
            <option value="Debt Service Coverage (DSC)">Debt Service Coverage (DSC)</option>
            <option value="Book Leverage - Debt/ TNW">Book Leverage - Debt/ TNW</option>
            <option value="Return on Equity (ROE)">Return on Equity (ROE)</option>
            <option value="Cashflow Leverage (Debt / EBITDA)">Cashflow Leverage (Debt / EBITDA)</option>
            <option value="Notes to financial statement">Notes to financial statement</option>
          </select>

          <div className="html-content-container"
            dangerouslySetInnerHTML={{ __html: getHtmlContent() }} style={{ maxHeight: '50%', overflow: 'scroll' }} />
          {/* Notes Panel */}
          <div style={{ flex: 0.25, borderTop: '1px solid #ccc', paddingTop: '20px' }}>
            <h3>Note Details</h3>
            {selectedNote ? (
              <div>{selectedNote}</div>
            ) : (
              <p>No note selected</p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default ResultsScreen;
