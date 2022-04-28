import React from 'react';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect
} from "react-router-dom";

import Login from './Login';
import Register from './Register';
import Activate from './Activate';
import ForgotPassword from './ForgotPassword';
import PasswordReset from './PasswordReset';

function UnAuthed() {
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
  );
}

export default UnAuthed;