import React from 'react';

import { Container, Row, Col } from 'react-bootstrap';

import ChangePassword from './ChangePassword';
import ChangeDetails from './ChangeDetails';

function Settings() {
  return (
    <Container className="mt-4">
      <Row className="justify-content-md-center">
        <Col sm={12}>
          <div className="display-4 text-center my-4">
            Settings
          </div>
        </Col>
      </Row>
      <Row className="justify-content-md-center">
        <Col md={6} xl={4}>
          <ChangeDetails />
        </Col>
        <Col md={6} xl={4}>
          <ChangePassword />
        </Col>
      </Row>
    </Container>
  );
} 

export default Settings;