import React from 'react';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Form from 'react-bootstrap/Form'       
import Button from 'react-bootstrap/Button'     
import FormControl from 'react-bootstrap/FormControl'

import { withNamedStores } from './store/state';

import './App.css';

const App = function (props) {
  console.debug('APP props', props)

  if (props.user === undefined) {
    return (
      <div className="main-container">
        <div className="main-item" style={{height: "100%"}}>
          <Login />
        </div>
      </div>
    )
  }

  return (
    <Router>
      <div className="main-container">

        <Navbar className="main-item" bg="dark" variant="dark">
          <Navbar.Brand>
            <Nav.Link as={Link} to="/">Home</Nav.Link>
          </Navbar.Brand>
          <Nav className="mr-auto">
            <Nav.Link to="/" as={Link}>Dashboard</Nav.Link>
          </Nav>
          <Form inline>
            <FormControl type="text" placeholder="Search" className="mr-sm-2" />
            <Button variant="outline-info">Search</Button>
          </Form>
        </Navbar>

        <div className="main-item" style={{height: "100%"}}>
          <Switch>
            <Route path="/login">
              <Login />
            </Route>
            <Route path="/">
              <Dashboard />
            </Route>
          </Switch>
        </div>
      </div>
    </Router>
  );
}

export default withNamedStores(App, ['user']);