import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Container, Navbar, Button, Form } from 'react-bootstrap';

function UploadScreen({ onUpload }) {
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);
    console.log(file);  // Log response data
  
    try {
      const response = await axios.post('http://127.0.0.1:5000/upload', formData);
      const responseData = response.data;  // This is where you define responseData
      console.log("Upload successful", file);  // Log response data
      
      // Create a local URL for the file
      const fileURL = URL.createObjectURL(file);
      
      onUpload(fileURL);  // Pass the data to parent or wherever needed

      console.log("FileURL", fileURL);  // Log response data

      navigate('/results', { state: { fileURL } });  // Navigate to ResultScreen with the data
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
