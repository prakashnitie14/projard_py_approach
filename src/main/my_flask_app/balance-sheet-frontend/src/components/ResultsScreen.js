import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar, Nav } from 'react-bootstrap';
import { useLocation } from 'react-router-dom';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

// Assuming data is passed as a prop
const ResultsScreen = ({ data }) => {
  const [selectedOption, setSelectedOption] = React.useState('Income Statement');
  const navigate = useNavigate();
  const location = useLocation();
  const { fileURL } = location.state || {}; // Get file URL from state

  // Debugging: Check if data is received correctly
  console.log('This is the fileURL', fileURL);

  if (!data) {
    navigate('/upload');
    return null;
  }

  const defaultLayoutPluginInstance = defaultLayoutPlugin();

  const extractCompanyName = (htmlString) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');
    const divs = doc.querySelectorAll('div');

    for (let i = 0; i < divs.length; i++) {
      if (divs[i].textContent.includes('Company Name')) {
        return divs[i + 1] ? divs[i + 1].textContent : 'N/A';
      }
    }

    return 'N/A';
  };

  const extractQuality = (htmlString) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');
    const divs = doc.querySelectorAll('div');

    for (let i = 0; i < divs.length; i++) {
      if (divs[i].textContent.includes('Financial Statement Quality')) {
        return divs[i + 1] ? divs[i + 1].textContent : 'N/A';
      }
    }

    return 'N/A';
  };

  const getHtmlTable = (htmlString, headingText) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');
    const headings = doc.querySelectorAll('h2');
    let targetTable = null;

    headings.forEach(heading => {
      if (heading.textContent.includes(headingText)) {
        let sibling = heading.nextElementSibling;
        while (sibling) {
          if (sibling.tagName === 'TABLE') {
            targetTable = sibling.outerHTML;
            break;
          }
          sibling = sibling.nextElementSibling;
        }
      }
    });

    return targetTable || '<p>No data available</p>';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
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
        <div style={{ flex: 1, padding: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <strong>Company Name:</strong>
              <div>{extractCompanyName(data)}</div>
            </div>
            <div>
              <strong>Financial Statement Quality:</strong>
              <div>{extractQuality(data)}</div>
            </div>
          </div>
          <select onChange={(e) => setSelectedOption(e.target.value)} value={selectedOption} style={{ marginTop: '20px' }}>
            <option value="Income Statement">Income Statement</option>
            <option value="Balance Sheet">Balance Sheet</option>
            <option value="Cashflow Statement (if available)">Cashflow Statement (if available)</option>
            <option value="Operating Financial Metrics">Operating Financial Metrics</option>
            <option value="Debt Service Coverage (DSC)">Debt Service Coverage (DSC)</option>
            <option value="Book Leverage - Debt/ TNW">Book Leverage - Debt/ TNW</option>
            <option value="Return on Equity (ROE)">Return on Equity (ROE)</option>
            <option value="Cashflow Leverage (Debt / EBITDA)">Cashflow Leverage (Debt / EBITDA)</option>
          </select>

          <div dangerouslySetInnerHTML={{ __html: getHtmlTable(data, selectedOption) }} />
        </div>
      </div>
    </div>
  );
};

export default ResultsScreen;
