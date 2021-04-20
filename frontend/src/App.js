import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect
} from "react-router-dom";

import Login from './pages/Login';
import Register from './pages/Register';
import Activate from './pages/Activate';
import ForgotPassword from './pages/ForgotPassword';
import Main from './pages/Main';
import NotFound from './pages/NotFound';
import PasswordReset from './pages/PasswordReset';
import SideBar from './pages/SideBar';
import Settings from './pages/Settings';
import TopNav from './pages/TopNav';

import { getUserData } from './api/requests';
import { withNamedStores } from './store/state';

import './App.css';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


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
          <div className="text-center">
            <div style={{marginTop: "50vh"}} className="h1">
              Loading...
            </div>
        </div>
      </Router>
    )
  }

  if (props.user === undefined) {
    return (
      <Router>
        <Switch>
          <Route exact path="/"><Login /></Route>
          <Route path="/login"><Login /></Route>
          <Route path="/register"><Register /></Route>
          <Route path="/activate/:activation_key"><Activate /></Route>
          <Route path="/forgot_password"><ForgotPassword /></Route>
          <Route path="/password_reset/:reset_key"><PasswordReset /></Route>
          <Route path="*"><Redirect to="/" /></Route>
        </Switch>
      </Router>
    )
  }

  return (
    <Router>
        <TopNav />

        <Container fluid>
          <Row>
              <Col md={2} className="d-none d-md-block bg-light sidebar">
                <SideBar />
              </Col>
              <main role="main" className="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3">
                  <Switch>
                    <Route path="/activate/:activation_key"><Activate /></Route>
                    <Route path="/login"><Redirect push to="/" /></Route>
                    <Route exact path="/"><Main /></Route>
                    <Route exact path="/settings"><Settings /></Route>
                    <Route path="*"><NotFound /></Route>
                  </Switch>
                </div>
              </main>
          </Row>
        </Container>
    </Router>
  );
}

App.propTypes = {
  dispatch: PropTypes.func.isRequired,
  loaded: PropTypes.bool.isRequired,
  user: PropTypes.shape({
    display_name: PropTypes.string.isRequired,
  })
}

export default withNamedStores(App, ['user', 'dispatch', 'logout_url']);