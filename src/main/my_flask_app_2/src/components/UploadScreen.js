import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Container, Navbar, Button, Form } from 'react-bootstrap';

function UploadScreen({ onUpload }) {
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  // Handle file input change
  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  // Handle file upload and send data to backend
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file to upload");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Send file to the backend
      const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const responseData = response.data;  // Response from backend (results)

      // Create a local URL for the uploaded PDF file
      const fileURL = URL.createObjectURL(file);

      // Pass the file URL and response data to ResultsScreen
      navigate('/results', { state: { fileURL, responseData } });

    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div>
      <Navbar bg="light" expand="lg">
        <Container>
          <Navbar.Brand href="#">TARS V1</Navbar.Brand>
        </Container>
      </Navbar>

      <Container className="text-center mt-5" style={{ marginTop: '30vh' }}>
        <h2>Advanced Financial Statement Analysis Tool</h2>
      </Container>

      <Container className="text-center" style={{ marginTop: '40vh' }}>
        <Form>
          <Form.Group controlId="formFile" className="mb-3">
            <Form.Control type="file" onChange={handleFileChange} />
          </Form.Group>
          <Button variant="primary" onClick={handleUpload}>
            Upload
          </Button>
        </Form>
      </Container>
    </div>
  );
}

export default UploadScreen;
