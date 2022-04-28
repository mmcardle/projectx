
import React from 'react';
import { withNamedStores } from '../store/state';
import { Link } from "react-router-dom";

import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';

function SideBar(props) {
  const flex = props.as_rows ? "flex-row" : "flex-column";
  const fixed = props.fixed ? props.fixed : "";
  return (
    <div>
      <Navbar fixed={fixed} bg="light" expand="lg">
        <Nav defaultActiveKey="/home" className={flex} >
          <Nav.Link className="mr-2" as={Link} to="/">Projects</Nav.Link>
          <Nav.Link className="mr-2" as={Link} to="/settings">Settings</Nav.Link>
        </Nav>
      </Navbar>
    </div>
  );
}

export default withNamedStores(SideBar, ['user']);