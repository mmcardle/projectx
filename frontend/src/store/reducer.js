
import { create_websocket } from '../websocket';
import actions from './actions';

const initialState = {
  loaded: false,
  user: undefined,
  token: undefined,
  logout_url: undefined,
  websocket: undefined,
};

const Reducer = (state, action) => {
  console.debug(action.type, action);
  switch (action.type) {
    case actions.SET_USER: {
      const { user, logout_url, token } = action;
      const websocket = create_websocket();
      return {
        ...state,
        user,
        logout_url,
        token,
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
      return state;
  }
};


export { Reducer, initialState };