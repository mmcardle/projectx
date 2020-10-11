import React from 'react';

import { withNamedStores } from '../store/state';

import { postJSON, fetchToken, loadUser } from '../requests';
import { login_url } from '../urls';

import Form from 'react-bootstrap/Form';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

import './Login.css';

function Login(props) {

  function login(email, password) {
    fetchToken().then((token) => {
      // handle success
      console.debug('Get user data', token);
      postJSON(
        login_url,
        { email, password },
        { headers: { 'X-CSRFToken': token } },
      ).then((data) => {
        //this.setState({ error: undefined });
        const { dispatch } = props;
        loadUser(dispatch, data.user, data.logout_url, data.token);
      }).catch((error) => {
        console.error('Could not log in', error);
        //this.setState({ error: "Sorry we couldn't log you in at this time, please check email and password." });
      });
    }).catch((error) => {
      console.error('Could not log in', error);
      //this.setState({ error: "Sorry we couldn't log you in at this time." });
    });
  }

  function click(e) {
    e.preventDefault();
    login("none@none.com", "pass")
  }

  return (
    <div className="login-container mt-5">
      <Card className="login-item" bg="dark" text="white" border="secondary" style={{ width: '25rem' }} >
        <Card.Img variant="top" src="logo.svg" className="p-2 w-50 m-auto" />
        <Card.Body>
          <Card.Title className="text-center display-3">Project X</Card.Title>
          <Card.Body>
            <Form>
              <Form.Group controlId="formBasicEmail">
                <Form.Label>Email address</Form.Label>
                <Form.Control type="email" placeholder="Enter email" />
                <Form.Text className="text-muted">
                  We'll never share your email with anyone else.
                </Form.Text>
              </Form.Group>

              <Form.Group controlId="formBasicPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control type="password" placeholder="Password" />
              </Form.Group>
              <Form.Group controlId="formBasicCheckbox">
                <Form.Check type="checkbox" label="Check me out" />
              </Form.Group>
              <Button block variant="primary" onClick={click}>
                Login
              </Button>
            </Form>
          </Card.Body>
        </Card.Body>
      </Card>
    </div>
  );
}

export default withNamedStores(Login, ['dispatch']);
