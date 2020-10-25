
import React from 'react';
import { withNamedStores } from '../store/state';
import { Link } from "react-router-dom";

import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

import { logout } from '../api/requests';

function TopNav(props) {
  console.debug("TopNav", props)

  function logout_click(e) {
    e.preventDefault();
    logout(props.dispatch, props.logout_url);
  }

  return (
    <Navbar className="main-item" bg="dark" variant="dark">
      <Navbar.Brand>
        <Nav.Link as={Link} to="/" className="h4">{process.env.REACT_APP_PROJECT_TITLE}</Nav.Link>
      </Navbar.Brand>
      <Nav className="mr-auto">
      </Nav>
      <Form inline onSubmit={logout_click}>
        <Button variant="outline-secondary" type="submit">Logout</Button>
      </Form>
    </Navbar>
  );
}

export default withNamedStores(TopNav, ['user', 'dispatch']);