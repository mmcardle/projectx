import React from 'react';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect
} from "react-router-dom";

import Activate from './Activate';
import Dashboard from './Dashboard';
import NotFound from './NotFound';
import SideBar from './SideBar';
import Settings from './Settings';
import TopNav from './TopNav';
import Example from './Example';

import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

function Authed() {
  return (
    <Router>
        <TopNav />

        <Container fluid>
          <Row>
              <Col md={2} className="d-none d-md-block bg-light sidebar pt-5">
                <SideBar />
              </Col>
              <Col col={12} className="d-md-none bg-light pt-5">
                <SideBar as_rows fixed="bottom" />
              </Col>
              <Col md={10} xs={12} className="ml-sm-auto px-4">
                <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 py-5">
                  <Switch>
                    <Route path="/activate/:activation_key"><Activate /></Route>
                    <Route path="/login"><Redirect push to="/" /></Route>
                    <Route exact path="/"><Dashboard /></Route>
                    <Route path="/example"><Example /></Route>
                    <Route exact path="/settings"><Settings /></Route>
                    <Route path="*"><NotFound /></Route>
                  </Switch>
                </div>
              </Col>
              
          </Row>
        </Container>
    </Router>
  );
}

export default Authed;