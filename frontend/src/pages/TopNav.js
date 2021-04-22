import React from 'react';
import { withNamedStores } from '../store/state';
import PropTypes from 'prop-types';

import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Form from 'react-bootstrap/Form';

import { logout } from '../api/requests';

function TopNav(props) {
  console.debug("TopNav", props)

  function logout_click(e) {
    e.preventDefault();
    logout(props.dispatch, props.logout_url);
  }

  return (
    <Navbar className="sticky-top flex-md-nowrap p-0" bg="dark" variant="dark">
      <Navbar.Brand className="col-sm-3 col-md-2 mr-0">
        <Nav.Link to="/" className="text-white p-0">{process.env.REACT_APP_PROJECT_TITLE}</Nav.Link>
      </Navbar.Brand>
      <Form.Control className="form-control-dark w-100" type="text" placeholder="Search" />
      <Nav className="mr-auto">
      </Nav>
      <Nav className="px-3">
        <Nav.Item>
          <Nav.Link onClick={logout_click} className="nav-link" variant="link">Logout</Nav.Link>
        </Nav.Item>
      </Nav>
    </Navbar>
  );
}

TopNav.propTypes = {
  dispatch: PropTypes.func.isRequired,
  logout_url: PropTypes.string.isRequired,
}

export default withNamedStores(TopNav, ['user', 'dispatch']);