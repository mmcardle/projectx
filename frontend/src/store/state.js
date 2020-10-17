import React, { useContext, createContext, useReducer } from 'react';
import PropTypes from 'prop-types';

import { initialState, Reducer } from './reducer';

const Store = ({ children }) => {
  const [state, dispatch] = useReducer(Reducer, initialState);
  return (
    <Context.Provider value={[state, dispatch]}>
      {children}
    </Context.Provider>
  );
};

Store.propTypes = {
  children: PropTypes.node.isRequired,
};

const Context = createContext(initialState);

function useUserStore() {
  const store = useContext(Context)[0];
  return {
    user: store.user,
    websocket: store.websocket,
    loaded: store.loaded,
    current_project: store.current_project,
    logout_url: store.logout_url,
  };
}

function useDispatchStore() {
  const dispatch = useContext(Context)[1];
  return { dispatch };
}

function useKeyfromStore(key) {
  const { [key]: val } = useContext(Context)[0];
  return { [key]: val };
}

const storeNames = {
  user:  (Component) => (props) => <Component {...useUserStore()} {...props} />,
  token:  (Component) => (props) => <Component {...useKeyfromStore('token')} {...props} />,
  dispatch: (Component) => (props) => <Component {...useDispatchStore()} {...props} />,
  logout_url: (Component) => (props) => <Component {...useKeyfromStore('logout_url')} {...props} />
};

// Applies multiple stores to a Component
const withNamedStores = (Component, stores) => {
  let storeComponent = Component;
  stores.forEach((storeName) => {
    if (storeNames[storeName] !== undefined) {
      storeComponent = storeNames[storeName](storeComponent);
    } else {
      console.error(`Unknown Store ${storeName}`);
    }
  });
  return storeComponent;
};

export { Store, withNamedStores };