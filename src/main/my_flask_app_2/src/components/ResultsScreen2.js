import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Navbar, Nav } from 'react-bootstrap';
import { Viewer, Worker } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import './resultsScreen.css';

const ResultsScreen = () => {
    const [selectedOption, setSelectedOption] = useState('Income Statement');
    const [selectedNote, setSelectedNote] = useState(null); // For storing the selected note
    const navigate = useNavigate();
    const location = useLocation();
    const { fileURL, responseData } = location.state || {}; // Get file URL and response data from state

    // If no data, navigate back to upload screen
    useEffect(() => {
        if (!fileURL || !responseData) {
            navigate('/upload');
        }
    }, [fileURL, responseData, navigate]);

    // Function to handle note clicks
    const handleNoteClick = (noteContent, event) => {
        event.preventDefault();
        setSelectedNote(noteContent);
    };

    // Function to apply color coding and convert to React structure
    const applyColorCoding = (tableData) => {
        if (!tableData) return null;
        const rows = tableData.split('\n').map((row, rowIndex) => {
            const cells = row.split(',');

            const growthFallValue = parseFloat(cells[5]?.replace('%', '').trim());
            const colCStyle = growthFallValue > 10 ? { backgroundColor: 'red' } : {};

            return (
                <tr key={rowIndex}>
                    <td>{cells[0]}</td>
                    <td>{cells[1]}</td>
                    <td>
                        {cells[2] ? (
                            <a href="#" onClick={(e) => handleNoteClick(cells[2], e)}>
                                {cells[2]}
                            </a>
                        ) : null}
                    </td>
                    <td>{cells[3]}</td>
                    <td>{cells[4]}</td>
                    <td>{cells[5]}</td>
                    <td style={colCStyle}>{cells[6]}</td>
                </tr>
            );
        });

        return (
            <table>
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th>Notes</th>
                        <th>Current year</th>
                        <th>Previous year</th>
                        <th>Growth/Fall</th>
                        <th>Column C</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        );
    };

    const getHtmlContent = () => {
        switch (selectedOption) {
            case 'Income Statement':
                console.log(responseData.income_statement)
                return applyColorCoding(responseData.income_statement);
            case 'Balance Sheet':
                return applyColorCoding(responseData.balance_sheet);
            // Add more cases as needed for other financial statements
            default:
                return <p>No data available</p>;
        }
    };

    const defaultLayoutPluginInstance = defaultLayoutPlugin();

    return (
        <div style={{ flex: '1', display: 'flex', flexDirection: 'column', height: '100vh' }}>
            {/* Navbar */}
            <Navbar bg="light" expand="lg">
                <Navbar.Brand href="/">TARS V1</Navbar.Brand>
                <Nav className="ml-auto"></Nav>
            </Navbar>

            <div style={{ display: 'flex', flex: 1 }}>
                {/* Left Segment */}
                <div style={{ flex: 1, padding: '20px', borderRight: '1px solid #ccc' }}>
                    <h2>Copy of the Uploaded Financial Statement</h2>
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
                        onChange={(e) => setSelectedOption(e.target.value)}
                        value={selectedOption}
                        style={{ marginTop: '20px' }}
                    >
                        <option value="Income Statement">Income Statement</option>
                        <option value="Balance Sheet">Balance Sheet</option>
                        {/* Add more options as needed */}
                    </select>

                    <div style={{ maxHeight: '50%', overflow: 'scroll' }}>
                        {getHtmlContent()}
                    </div>

                    {/* Notes Panel */}
                    <div style={{ flex: 0.25, borderTop: '1px solid #ccc', paddingTop: '20px' }}>
                        <h3>Note Details</h3>
                        {selectedNote ? <div>{selectedNote}</div> : <p>No note selected</p>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResultsScreen;
