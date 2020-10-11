
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
      return {
        ...state,
        user,
        logout_url,
        token,
      };
    }
    case actions.SET_LOADED: {
      // TODO websocket
      console.log('TODO Need to call', create_websocket)
      //const websocket = create_websocket();
      return {
        ...state,
        loaded: true,
        //websocket,
      };
    }
    case actions.SET_LOGGED_OUT: {
      const { websocket } = state;
      websocket.close();
      return {
        ...initialState,
      };
    }
    default:
      return state;
  }
};


export { Reducer, initialState };