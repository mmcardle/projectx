import React, { useState, useEffect } from 'react';
import {
  Link, useParams
} from "react-router-dom";
import { withNamedStores } from '../store/state';
import { postJSON, fetchToken } from '../api/requests';
import { activate_url } from '../api/urls';

import CentralContainer from '../containers/CentralContainer'

import Alert from 'react-bootstrap/Alert';

function PasswordReset(props) {
  console.debug('PasswordReset', props)

  const [complete, setComplete] = useState(false)
  const [error, setError] = useState(undefined)
  const { activation_key } = useParams();

  const [activating, setActivating] = useState(false);

  useEffect(() => {
    if (!activating) {
      setActivating(true)
      const params = {activation_key};

      fetchToken().then((token) => {
        postJSON(
          activate_url, params, { headers: { 'X-CSRFToken': token } },
        ).then((data) => {
          setComplete(true);
        }).catch((error) => {
          setError('Sorry, there has been an issue activating your account. Your token may have expired');
          console.debug('Could not activate account', error);
        });
      });
    }
  }, [activating, activation_key, props.dispatch]);

  if (error) {
    return <CentralContainer><Alert variant="danger">{error}</Alert></CentralContainer>;
  }
  
  if (complete) {
    return (
      <CentralContainer>
        <Alert variant="info">
          Your account has been activated. You may now <Link className="text-muted" to="/">Login</Link>.
        </Alert> 
      </CentralContainer>
    )
  } else {
    return <CentralContainer><div className="text-center">Activating ...</div></CentralContainer>
  }
}

export default withNamedStores(PasswordReset, ['dispatch']);
