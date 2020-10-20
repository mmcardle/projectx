import React from 'react';

import { Container, Row, Col } from 'react-bootstrap';

import ChangePassword from './ChangePassword';
import ChangeDetails from './ChangeDetails';

function Settings(props) {
  return (
    <div className="main-content-item">
      <Container className="text-white">
        <Row>
          <Col className="p-3 my-1 border border-secondary rounded bg-dark">
            <h1>Settings</h1>
          </Col>
        </Row>
        <Row>
          <Col sm={4} className="p-3 border border-secondary rounded bg-dark">
            <ChangeDetails />
          </Col>
          <Col sm={4} className="p-3 border border-secondary rounded bg-dark">
            <ChangePassword />
          </Col>
          <Col sm={4} className="p-3 border border-secondary rounded bg-dark">
          </Col>
        </Row>
      </Container>
    </div>
  );
} 

export default Settings;