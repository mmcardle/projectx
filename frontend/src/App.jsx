import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

import Loading from './pages/Loading';
import UnAuthed from './pages/UnAuthed';
import Authed from './pages/Authed';

import { getUserData } from './api/requests';
import { withNamedStores } from './store/state';
import './theme_1618955931948.css' // https://themestr.app/
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
    return <Loading />;
  }

  if (props.user === undefined) {
    return <UnAuthed />
  }

  return <Authed />;
}

App.propTypes = {
  dispatch: PropTypes.func.isRequired,
  loaded: PropTypes.bool.isRequired,
  user: PropTypes.shape({
    display_name: PropTypes.string.isRequired,
  })
}

export default withNamedStores(App, ['user', 'dispatch', 'logout_url']);