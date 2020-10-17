import React, { useState } from 'react';
import { Link } from "react-router-dom";
import { withNamedStores } from '../store/state';

import { forgotPassword } from '../api/requests';

import CentralContainer from '../containers/CentralContainer'

import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

function ForgotPassword(props) {

  const [email, setEmail] = useState("")
  const [complete, setComplete] = useState(false)
  const [error, setError] = useState(undefined)

  function click(e) {
    e.preventDefault();
    setError(undefined);
    forgotPassword(email).then(() => {
      setComplete(true)
    }).catch((error) => {
      console.log('Could not reset password', error);
      setError('Sorry we could not reset your password at this time. Please try again in a few minutes.');
    })
  }

  return (
    <CentralContainer>
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
    </CentralContainer>
  );
}

export default withNamedStores(ForgotPassword, ['dispatch']);
