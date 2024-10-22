import React from 'react';
import MyNavbar from './MyNavbar';
import MyCard from './MyCard';
import MyButton from './MyButton';
import { Container, Row, Col } from 'react-bootstrap';

function TestLayout() {
  return (
    <div>
      <MyNavbar />
      <Container>
        <Row>
          <Col md={4}>
            <MyCard />
          </Col>
          <Col md={4}>
            <MyCard />
          </Col>
          <Col md={4}>
            <MyCard />
          </Col>
        </Row>
        <Row>
          <Col>
            <MyButton />
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default TestLayout;
