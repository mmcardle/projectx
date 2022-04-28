import React, {useReducer} from 'react';
import { withNamedStores } from '../store/state';
import PropTypes from 'prop-types';
import { Link } from "react-router-dom";
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Form from 'react-bootstrap/Form';
import { logout } from '../api/requests';

const title = import.meta.env.VITE_APP_PROJECT_TITLE

function TopNav(props) {
  console.debug("TopNav", props)
  
  function logout_click(e) {
    e.preventDefault();
    logout(props.dispatch, props.logout_url);
  }

  return (
    <Navbar className="p-0" fixed="top" bg="dark" variant="dark" >
      <Navbar.Brand className="col-4 col-md-3 offset-lg-2 col-lg-2 mr-0">
        <Nav.Link to="/" as={Link} className="text-white p-0 pl-4">{title}</Nav.Link>
      </Navbar.Brand>
      <Form.Control className="d-none form-control-dark w-100" type="text" placeholder="Search" />
      <Nav className="col-8 col-md-9 col-lg-7 col-xl-6">
        <Nav.Item>
          <Nav.Link className="mx-2" as={Link} to="/">Projects</Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link className="mx-2" as={Link} to="/settings">Settings</Nav.Link>
        </Nav.Item>
        <Navbar.Text className="bg-danger p-2 text-white m-auto px-4 rounded-pill text-monospace">
          Beta
        </Navbar.Text>
        <Nav.Item className="ml-auto">
          <Nav.Link onClick={logout_click} className="nav-link" variant="link">Logout</Nav.Link>
        </Nav.Item>
      </Nav>
      <Nav className="px-3">
      </Nav>
    </Navbar>
  );
}

TopNav.propTypes = {
  dispatch: PropTypes.func.isRequired,
  logout_url: PropTypes.string.isRequired,
}

export default withNamedStores(TopNav, ['user', 'dispatch']);