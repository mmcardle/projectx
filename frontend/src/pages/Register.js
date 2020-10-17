import React, { useState } from 'react';
import { Link } from "react-router-dom";

import { register } from '../api/requests';

import CentralContainer from '../containers/CentralContainer'

import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

function Register() {

  const [email, setEmail] = useState("")
  const [password1, setPassword1] = useState("")
  const [password2, setPassword2] = useState("")
  const [first_name, setFirstName] = useState("")
  const [last_name, setLastName] = useState("")
  const [error, setError] = useState(undefined)
  const [complete, setComplete] = useState(false)

  function click(e) {
    e.preventDefault();
    setError(undefined);
    register(email, password1, password2, first_name, last_name).then(() => {
      setComplete(true)
    }).catch((error) => {
      console.error('Could not register.', error);
      setError("Sorry we couldn't register you at this time.");
    });
  }

  if (complete) {
    return (
      <CentralContainer>
        <Alert variant="info">
          Your account has been created.
          Please click the link in the email to active your account.
        </Alert>
      </CentralContainer>
    )
  }

  return (
    <CentralContainer>
      <Form onSubmit={click}>
        { error ? <Alert variant="danger">{error}</Alert> : <></> }
        <Form.Group controlId="registerEmail">
          <Form.Label>Email address</Form.Label>
          <Form.Control required type="email" placeholder="Enter email" value={email} onChange={e => setEmail(e.target.value)} />
        </Form.Group>
        <Form.Group controlId="registerLastName">
          <Form.Label className="d-none sr-block">First Name</Form.Label>
          <Form.Control required type="text" placeholder="First Name" value={first_name} onChange={e => setFirstName(e.target.value)} />
        </Form.Group>
        <Form.Group controlId="registerFirstName">
          <Form.Label className="d-none sr-block">Last Name</Form.Label>
          <Form.Control required type="text" placeholder="Last Name" value={last_name} onChange={e => setLastName(e.target.value)} />
        </Form.Group>
        <Form.Group controlId="registerPassword1">
          <Form.Label>Password</Form.Label>
          <Form.Control required type="password" placeholder="Password" value={password1} onChange={e => setPassword1(e.target.value)} />
        </Form.Group>
        <Form.Group controlId="registerPassword2">
          <Form.Label className="d-none sr-block">Password Again</Form.Label>
          <Form.Control required type="password" placeholder="Password Again" value={password2} onChange={e => setPassword2(e.target.value)} />
        </Form.Group>
        <Button block variant="primary" type="submit">
          Register
        </Button>
      </Form>
      <div className="text-center mt-2" >
        <Link to="/login">Login</Link>
      </div>
    </CentralContainer>
  );
}

export default Register;
