import React, { useState } from 'react';
import { Link } from "react-router-dom";
import { withNamedStores } from '../store/state';

import { postJSON, fetchToken } from '../api/requests';
import { forgot_password_url } from '../api/urls';

import CentralContainer from '../containers/CentralContainer'

import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

function ForgotPassword(props) {

  const [email, setEmail] = useState("")
  const [complete, setComplete] = useState(false)
  const [error, setError] = useState(undefined)

  function forgotPassword(email) {
    setError(undefined);
    fetchToken().then((token) => {
      postJSON(
        forgot_password_url, { email }, { headers: { 'X-CSRFToken': token } },
      ).then(() => {
        setComplete(true)
      }).catch((error) => {
        console.error('Could not reset password', error);
        setError('Sorry we could not reset your password at this time. Please try again in a few minutes.');
      });
    });
  }

  function click(e) {
    e.preventDefault();
    forgotPassword(email)
  }

  return (
    <CentralContainer>
      <Card bg="dark" text="white" border="secondary" style={{ width: '25rem' }} >
        <Card.Img variant="top" src="logo.svg" className="p-2 w-50 m-auto" />
        <Card.Body>
          <Card.Title className="text-center display-3">Project X</Card.Title>
          <Card.Body>
            <Form onSubmit={click}>
              { error ? <Alert variant="danger">{error}</Alert> : <></> }
              <Form.Group controlId="forgotPasswordEmail">
                <Form.Label>Email address</Form.Label>
                <Form.Control required type="email" placeholder="Enter email" value={email} onChange={e => setEmail(e.target.value)} />
                <Form.Text className="text-muted">
                  We'll never share your email with anyone else.
                </Form.Text>
              </Form.Group>
              {
                complete ?
                <Alert variant="info">
                  A password reset email has been sent to the email address.
                </Alert> :
                <Button block variant="primary" type="submit">
                  Submit Password Reset
                </Button>
              }
            </Form>
            <div className="text-center mt-2" >
              <Link to="/login" className="text-muted">Back to Login</Link>
            </div>
          </Card.Body>
        </Card.Body>
      </Card>
    </CentralContainer>
  );
}

export default withNamedStores(ForgotPassword, ['dispatch']);
