import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

import Loading from './pages/Loading';
import UnAuthed from './pages/UnAuthed';
import Authed from './pages/Authed';

import { getUserData } from './api/requests';
import { withNamedStores } from './store/state';

import './theme_1618955931948.css'
import './App.css';


const App = function (props) {
  console.debug('APP props', props)

  const [loadingUser, setLoadingUser] = useState(null);
  const [projectConfigLoaded, setProjectConfigLoaded] = useState(false);
  const [projectConfig, setProjectConfig] = useState({
    LoadingComponent: undefined,
    UnAuthedComponent: undefined,
    AuthedComponent: undefined,
  });

  useEffect(() => {
    if (!projectConfigLoaded) {
      import('./project/config').then(
        (projectConfigModule) => {
          setProjectConfig(projectConfigModule.default);
          setProjectConfigLoaded(true);
        }
      )
    }
  }, [projectConfigLoaded, projectConfig]);

  useEffect(() => {
    if (!loadingUser) {
      setLoadingUser(true)
      getUserData(props.dispatch)
    }
  }, [loadingUser, props.dispatch]);

  if (!props.loaded) {
    return (
      projectConfig.LoadingComponent ? projectConfig.LoadingComponent() : <Loading />
    )
  }

  if (props.user === undefined) {
    return (
      projectConfig.UnAuthedComponent ? projectConfig.UnAuthedComponent(): <UnAuthed />
    )
  }

  return (
    projectConfig?.AuthedComponent ? projectConfig.AuthedComponent(): <Authed />
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