import React, { useState, useEffect } from 'react';
import {
  Link, useParams
} from "react-router-dom";
import { withNamedStores } from '../store/state';
import { postJSON, fetchToken } from '../api/requests';
import { reset_password_check_url, reset_password_complete_url } from '../api/urls';

import CentralContainer from '../containers/CentralContainer'

import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';


const errorToMessage = (error) => {
  let errorMessage = '';
  if (error.response && error.response.data && error.response.data.errors) {
    errorMessage += ` ${Object.values(error.response.data.errors).join(', ')}`;
  }
  return errorMessage;
};

function PasswordReset(props) {
  console.debug('PasswordReset', props)

  const [email, setEmail] = useState(undefined)
  const [complete, setComplete] = useState(false)
  const [updatingPassword, setUpdatingPassword] = useState(false)
  const [password1, setPassword1] = useState("")
  const [password2, setPassword2] = useState("")
  const [error, setError] = useState(undefined)
  const [passwordError, setPasswordError] = useState(undefined)
  const { reset_key } = useParams();

  const [loadingResetKey, setLoadingResetKey] = useState(false);

  useEffect(() => {
    if (!loadingResetKey) {
      setLoadingResetKey(true)
      const params = {reset_key};

      fetchToken().then((token) => {
        postJSON(
          reset_password_check_url, params, { headers: { 'X-CSRFToken': token } },
        ).then((data) => {
          setEmail(data.email);
        }).catch((error) => {
          setError('Sorry, there has been an issue resetting your password. Your token may have expired');
          console.debug('Could not check reset key', error);
        });
      });
    }
  }, [loadingResetKey, reset_key, props.dispatch]);
 
  function click(e) {
    e.preventDefault();

    if (password1 !== password2) {
      setPasswordError('Sorry the passwords must match.');
      return;
    }
    
    setUpdatingPassword(true)
    const params = { reset_key, password1, password2 };

    fetchToken().then((token) => {
      postJSON(
        reset_password_complete_url, params, { headers: { 'X-CSRFToken': token } },
      ).then(() => {
        setUpdatingPassword(false)
        setComplete(true)
      }).catch((error) => {
        setError(`Sorry we could not reset your password. ${errorToMessage(error)}`);
        console.debug('Could not reset email', error);
      });
    });
  }


  const toCentral = (component) => {
    return (
      <CentralContainer>
        {component}
      </CentralContainer>
    )
  }

  if (error) {
    return toCentral(
      <>
        <Alert variant="danger">{error}</Alert>
        <div className="text-center mt-2" >
          <Link to="/forgot_password">Forgot Password</Link>
        </div>
      </>
    )
  }

  if (loadingResetKey && !email) {
    return toCentral(<div className="text-center">Loading...</div>)
  }

  if (updatingPassword && !email) {
    return toCentral( <div className="text-center">Updating Password....</div>)
  }

  if (complete) {
    return toCentral(
      <Alert variant="info">
        Your password has been reset. You may now <Link className="text-muted" to="/">Login</Link>.
      </Alert> 
    )
  }
  
  return toCentral(
    <Form onSubmit={click}>
      { passwordError ? <Alert variant="danger">{passwordError}</Alert> : <></> }
      <Form.Group controlId="passwordResetEmail">
        <Form.Label>Email address</Form.Label>
        <Form.Control autoComplete="email" readOnly type="email" placeholder="Loading Email..." value={email ||""} onChange={e => setEmail(e.target.value)} />
      </Form.Group>
      <Form.Group controlId="passwordResetPassword1">
        <Form.Label>Password</Form.Label>
        <Form.Control autoComplete="new-password" required type="password" placeholder="Password" value={password1} onChange={e => setPassword1(e.target.value)} />
      </Form.Group>
      <Form.Group controlId="passwordResetPassword2">
        <Form.Label>Password Again</Form.Label>
        <Form.Control autoComplete="new-password" required type="password" placeholder="Password Again" value={password2} onChange={e => setPassword2(e.target.value)} />
      </Form.Group>
      <Button block variant="primary" type="submit">
        Update Password
      </Button>
    </Form>
  )
}

export default withNamedStores(PasswordReset, ['dispatch']);
