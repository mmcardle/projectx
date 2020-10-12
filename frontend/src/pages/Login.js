import React, { useState } from 'react';
import { Link } from "react-router-dom";
import { withNamedStores } from '../store/state';

import { postJSON, fetchToken, loadUser } from '../api/requests';
import { login_url } from '../api/urls';

import CentralContainer from '../containers/CentralContainer'

import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

function Login(props) {

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState(undefined)

  function login(email, password) {
    setError(undefined);
    fetchToken().then((token) => {
      console.debug('Get user data', token);
      postJSON(
        login_url,
        { email, password },
        { headers: { 'X-CSRFToken': token } },
      ).then((data) => {
        const { dispatch } = props;
        loadUser(dispatch, data.user, data.logout_url, data.token)
      }).catch((error) => {
        console.error('Could not log in', error);
        setError("Sorry we couldn't log you in at this time, please check email and password.");
      });
    }).catch((error) => {
      console.error('Could not log in', error);
      setError("Sorry we couldn't log you in at this time.");
    });
  }

  function click(e) {
    e.preventDefault();
    login(email, password)
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
              <Form.Group controlId="loginEmail">
                <Form.Label>Email address</Form.Label>
                <Form.Control required type="email" placeholder="Enter email" value={email} onChange={e => setEmail(e.target.value)} />
                <Form.Text className="text-muted">
                  We'll never share your email with anyone else.
                </Form.Text>
              </Form.Group>
              <Form.Group controlId="loginPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control required type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
              </Form.Group>
              <Button block variant="primary" type="submit">
                Login
              </Button>
            </Form>
            <div className="text-center mt-2" >
              <Link to="/forgot_password">Forgot Password</Link>
            </div>
          </Card.Body>
        </Card.Body>
      </Card>
    </CentralContainer>
  );
}

export default withNamedStores(Login, ['dispatch']);
