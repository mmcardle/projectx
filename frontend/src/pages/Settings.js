import React, { useState } from 'react';

import { Container, Row, Col } from 'react-bootstrap';
import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

import { withNamedStores } from '../store/state';

function Settings(props) {

  const [currentPassword, setCurrentPassword] = useState("")
  const [password1, setPassword1] = useState("")
  const [password2, setPassword2] = useState("")
  const [error, setError] = useState(undefined)

  function click(e) {
    e.preventDefault()
    setError("IMCOMPLETE")
  }

  return (
    <div className="main-content-item">
      <Container >
        <Row>
          <Col className="p-3 my-2 bg-white border rounded">
            <h1>Settings</h1>
          </Col>
        </Row>
        <Row>
          <Col sm={4} className="p-3 bg-white border rounded">

            <h3>Change Password</h3>

            <Form onSubmit={click}>
              { error ? <Alert variant="danger">{error}</Alert> : <></> }
              <Form.Group controlId="currentPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control required type="password" placeholder="Password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} />
              </Form.Group>
              <Form.Group controlId="changePassword1">
                <Form.Label>Password</Form.Label>
                <Form.Control required type="password" placeholder="New Password" value={password1} onChange={e => setPassword1(e.target.value)} />
              </Form.Group>
              <Form.Group controlId="changePassword2">
                <Form.Label>Password</Form.Label>
                <Form.Control required type="password" placeholder="New Password Again" value={password2} onChange={e => setPassword2(e.target.value)} />
              </Form.Group>
              <Button block variant="primary" type="submit">
                Update
              </Button>
            </Form>

          </Col>
        </Row>
      </Container>
    </div>
  );
} 

export default withNamedStores(Settings, ['user']);