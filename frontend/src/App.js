import React, { useState, useEffect } from 'react';

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
import Dashboard from './pages/Dashboard';
import NotFound from './pages/NotFound';
import PasswordReset from './pages/PasswordReset';
import SideBar from './pages/SideBar';
import Settings from './pages/Settings';
import TopNav from './pages/TopNav';

import { getUserData } from './api/requests';
import { withNamedStores } from './store/state';

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
          <div className="main-item text-center">
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
          <div className="main-item">
            <Switch>
              <Route exact path="/"><Login /></Route>
              <Route path="/login"><Login /></Route>
              <Route path="/register"><Register /></Route>
              <Route path="/activate/:activation_key"><Activate /></Route>
              <Route path="/forgot_password"><ForgotPassword /></Route>
              <Route path="/password_reset/:reset_key"><PasswordReset /></Route>
              <Route path="*"><Redirect to="/" /></Route>
            </Switch>
          </div>
        </div>
      </Router>
    )
  }

  return (
    <Router>
      <div className="main-container">

        <TopNav />

        <div className="main-item">
          <div className="main-content">
            <SideBar />
            <Switch>
              <Route path="/activate/:activation_key"><Activate /></Route>
              <Route path="/login"><Redirect push to="/" /></Route>
              <Route exact path="/"><Dashboard /></Route>
              <Route exact path="/settings"><Settings /></Route>
              <Route path="*"><NotFound /></Route>
            </Switch>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default withNamedStores(App, ['user', 'dispatch', 'logout_url']);