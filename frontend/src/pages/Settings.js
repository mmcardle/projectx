import React from 'react';

import { Container, Row, Col } from 'react-bootstrap';

import ChangePassword from './ChangePassword';
import ChangeDetails from './ChangeDetails';

function Settings(props) {
  return (
    <div className="main-content-item">
      <Container >
        <Row>
          <Col className="p-3 my-2 bg-white border rounded">
            <h1>Settings</h1>
          </Col>
        </Row>
        <Row>
          <Col sm={4} className="p-3 m-1 bg-white border rounded">
            <ChangeDetails />
          </Col>
          <Col sm={4} className="p-3 m-1 bg-white border rounded">
            <ChangePassword />
          </Col>
        </Row>
      </Container>
    </div>
  );
} 

export default Settings;