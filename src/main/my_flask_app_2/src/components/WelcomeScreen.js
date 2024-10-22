import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Row, Col, Button, Navbar, Nav } from 'react-bootstrap';

const WelcomeScreen = () => {
  const navigate = useNavigate();

  const goToUpload = () => {
    navigate('/upload');
  };

  return (
    <div>
      <Navbar bg="light" expand="lg">
        <Container>
          <Navbar.Brand href="#">TARS V1</Navbar.Brand>
          <Nav className="ml-auto">
            <Button variant="outline-primary" onClick={goToUpload}>
              Demo
            </Button>
          </Nav>
        </Container>
      </Navbar>

      <Container className="text-center" style={{ marginTop: '20vh' }}>
        <h2>Advanced Financial Statement Analysis Tool</h2>
      </Container>

      <Container className="mt-4">
        <Row>
          <Col md={6} className="mb-4">
            <div className="p-3 border rounded text-center">
              Test Financial Metrics directly from a Financial Statement
            </div>
          </Col>
          <Col md={6} className="mb-4">
            <div className="p-3 border rounded text-center">
              How do the key ratios look?
            </div>
          </Col>
        </Row>
        <Row>
          <Col md={6} className="mb-4">
            <div className="p-3 border rounded text-center">
              View the Financial trend of the company
            </div>
          </Col>
          <Col md={6} className="mb-4">
            <div className="p-3 border rounded text-center">
              How much of cushion do the covenants have?
            </div>
          </Col>
        </Row>
      </Container>

      <Container className="text-center mt-5">
        <Button variant="primary" size="lg" onClick={goToUpload}>
          Upload Financial Statement
        </Button>
      </Container>
    </div>
  );
};

export default WelcomeScreen;