import React from 'react';

import { Container, Row, Col } from 'react-bootstrap';

import ChangePassword from './ChangePassword';
import ChangeDetails from './ChangeDetails';

function Settings() {
  return (
    <div className="main-content-item">
      <Container>
        <Row>
          <Col>
            <h1 className="my-1">Settings</h1>
          </Col>
        </Row>
        <Row>
          <Col sm={4} className="">
            <ChangeDetails />
          </Col>
          <Col sm={4} className="">
            <ChangePassword />
          </Col>
          <Col sm={4} className="">
          </Col>
        </Row>
      </Container>
    </div>
  );
} 

export default Settings;