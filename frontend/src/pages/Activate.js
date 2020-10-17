import React, { useState, useEffect } from 'react';
import {
  Link, useParams
} from "react-router-dom";
import { withNamedStores } from '../store/state';
import { activate } from '../api/requests';

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
      activate(activation_key).then(() => {
        setComplete(true);
      }).catch((error) => {
        console.error('Could not activate account', error);
        setError('Sorry, there has been an issue activating your account. Your token may have expired');
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
