
import React from 'react';
import { withNamedStores } from '../store/state';
import { Link } from "react-router-dom";

import Nav from 'react-bootstrap/Nav';

function SideBar(props) {
  return (
    <div className="main-sidebar p-2">
      <Nav defaultActiveKey="/home" className="flex-column" >
        <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
        <Nav.Link as={Link} to="/settings">Settings</Nav.Link>
        <Nav.Link as={Link} to="/account">Account</Nav.Link>
      </Nav>
    </div>
  );
}

export default withNamedStores(SideBar, ['user']);