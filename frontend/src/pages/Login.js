import React, { useState } from 'react';
import { Link } from "react-router-dom";
import { withNamedStores } from '../store/state';
import PropTypes from 'prop-types';

import { login } from '../api/requests';

import CentralContainer from '../containers/CentralContainer'

import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

function Login(props) {

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState(undefined)

  function click(e) {
    e.preventDefault();
    setError(undefined);
    login(
      props.dispatch, email, password
    ).catch(error => {
      console.error(error)
      setError("Sorry we couldn't log you in at this time, please check email and password.");
    })
  }

  return (
    <div className="mt-5">
      <CentralContainer >
        <Form onSubmit={click} id="login_form">
          { error ? <Alert variant="danger">{error}</Alert> : <></> }
          <Form.Group controlId="loginEmail">
            <Form.Label>Email address</Form.Label>
            <Form.Control required type="email" placeholder="Enter email" value={email} onChange={e => setEmail(e.target.value)} />
          </Form.Group>
          <Form.Group controlId="loginPassword">
            <Form.Label>Password</Form.Label>
            <Form.Control required type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
          </Form.Group>
          <Button block variant="primary" type="submit">
            Login
          </Button>
        </Form>
        <div className="text-center mt-2">
          <Link to="/register">
            <Button block variant="secondary">
              <span>Register Account</span>
            </Button>
          </Link>
        </div>
        <div className="text-center mt-2">
          <Link to="/forgot_password">Forgot Password</Link>
        </div>
      </CentralContainer>
    </div>
  );
}

Login.propTypes = {
  dispatch: PropTypes.func.isRequired,
}

export default withNamedStores(Login, ['dispatch']);
