import React, { useState, useEffect } from 'react';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  Redirect
} from "react-router-dom";

import Login from './pages/Login';
import Register from './pages/Register';
import Activate from './pages/Activate';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';

import actions from './store/actions';
import { getUserData } from './api/requests';
import { postJSON, fetchToken } from './api/requests';
import { withNamedStores } from './store/state';

import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Form from 'react-bootstrap/Form'       
import Button from 'react-bootstrap/Button'     
import NotFound from './pages/NotFound';
import PasswordReset from './pages/PasswordReset';

import './App.css';

const App = function (props) {
  console.debug('APP props', props)

  const [loadingUser, setLoadingUser] = useState(null);

  useEffect(() => {
    if (!loadingUser) {
      setLoadingUser(true)
      getUserData(props.dispatch)
    }
  }, [loadingUser, props.dispatch]);

  if (!props.loaded) {
    return (
      <Router>
        <div className="main-container">
          <div className="main-item text-center" style={{height: "100%"}}>
            <div style={{marginTop: "50vh"}} className="h1">
              Loading...
            </div>
          </div>
        </div>
      </Router>
    )
  }

  if (props.user === undefined) {
    return (
      <Router>
        <div className="main-container">
          <div className="main-item" style={{height: "100%"}}>
            <Switch>
              <Route exact path="/"><Login /></Route>
              <Route path="/login"><Login /></Route>
              <Route path="/register"><Register /></Route>
              <Route path="/activate/:activation_key"><Activate /></Route>
              <Route path="/forgot_password"><ForgotPassword /></Route>
              <Route path="/password_reset/:reset_key"><PasswordReset /></Route>
              <Route path="*"><NotFound /></Route>
            </Switch>
          </div>
        </div>
      </Router>
    )
  }

  function logout(e) {
    e.preventDefault();
    fetchToken().then((token) => {
      postJSON(
        props.logout_url, {}, { headers: { 'X-CSRFToken': token } },
      ).then(() => {
        props.dispatch({ type: actions.SET_LOGGED_OUT });
        setLoadingUser(true)
        getUserData(props.dispatch)
      }).catch((error) => {
        console.log('Could not log out', error);
      });
    });
  }


  return (
    <Router>
      <div className="main-container">

        <Navbar className="main-item" bg="dark" variant="dark">
          <Navbar.Brand>
            <Nav.Link as={Link} to="/" className="h4">ProjectX</Nav.Link>
          </Navbar.Brand>
          <Nav className="mr-auto">
            <Nav.Link to="/" as={Link}>Dashboard</Nav.Link>
          </Nav>
          <Form inline onSubmit={logout}>
            <Button variant="outline-secondary" type="submit">Logout</Button>
          </Form>
        </Navbar>

        <div className="main-item" style={{height: "100%"}}>
          <Switch>
            <Route path="/activate/:activation_key"><Activate /></Route>
            <Route path="/login"><Redirect push to="/" /></Route>
            <Route exact path="/"><Dashboard /></Route>
            <Route path="*"><NotFound /></Route>
          </Switch>
        </div>
      </div>
    </Router>
  );
}

export default withNamedStores(App, ['user', 'loading', 'dispatch', 'logout_url']);