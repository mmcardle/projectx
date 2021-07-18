
import { create_websocket } from '../websocket';
import actions from './actions';

const initialState = {
  loaded: false,
  user: undefined,
  token: undefined,
  jwt: undefined,
  logout_url: undefined,
  websocket: undefined,
  open_api: undefined,
};

const Reducer = (state, action) => {
  console.debug(action.type, action);
  switch (action.type) {
    case actions.SET_OPENAPI: {
      return {
        ...state,
        open_api: action.open_api_data,
      };
    }
    case actions.SET_USER: {
      const { user, logout_url, token, jwt } = action;
      const websocket = create_websocket();
      return {
        ...state,
        user,
        logout_url,
        token,
        jwt,
        loaded: true,
        websocket,
      };
    }
    case actions.SET_LOADED: {
      return {
        ...state,
        loaded: true,
      };
    }
    case actions.SET_LOGGED_OUT: {
      const { websocket } = state;
      if (websocket) websocket.close();
      return {
        ...initialState,
        loaded: true,
      };
    }
    default:
      console.debug('BAD ACTION', action.type, action);
      return state;
  }
};


export { Reducer, initialState };