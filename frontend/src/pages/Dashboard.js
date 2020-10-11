import React from 'react';
import { withNamedStores } from '../store/state';
import { Link } from "react-router-dom";

import Nav from 'react-bootstrap/Nav';

import './Dashboard.css'

function Dashboard(props) {
  return (
    <div className="dashboard-container">
      <div className="dashboard-sidebar p-2">
        <Nav defaultActiveKey="/home" className="flex-column" >
          <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
          <Nav.Link as={Link} to="/settings">Settings</Nav.Link>
          <Nav.Link as={Link} to="/account">Account</Nav.Link>
        </Nav>
      </div>
      <div className="dashboard-content text-center">
        <div className="bg-dark w-50 mx-auto rounded border border-secondary p-4 text-white" style={{marginBottom: "400px"}}>
          <img src="logo.svg" className="p-2 w-25 h-50 m-auto" />
          <div className="display-3">
            Welcome {props.user.display_name}
          </div>
          <div className="display-4">
            Email: {props.user.email}
          </div>
        </div>
      </div>
    </div>
  );
}

export default withNamedStores(Dashboard, ['user']);