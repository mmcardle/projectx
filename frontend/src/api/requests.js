
import axios from 'axios';

import actions from '../store/actions';
import { user_url, login_url } from './urls';

async function getJSON(url, args = {}) {
  const request_args = args;
  request_args.transformResponse = (data) => {
    console.debug(url, data);
    // Ensure data is valid json
    return JSON.parse(data);
  };
  const response = await axios.get(url, request_args);
  console.debug('GET from', url, request_args, ':', response.data);
  return response.data;
}

async function postJSON(url, params, args = {}) {
  const request_args = args;
  request_args.transformResponse = (data) => {
    console.debug(url, data);
    // Ensure data is valid json
    return JSON.parse(data);
  };
  const response = await axios.post(url, params, request_args);
  console.debug('POST to', url, request_args, ':', response.data);
  return response.data;
}

async function fetchToken() {
  try {
    const data = await getJSON(login_url);
    return Promise.resolve(data.token);
  } catch (error) {
    console.error(error);
    return Promise.reject(new Error('Could not fetch user data'));
  }
}

async function getUserData(dispatch) {
  try {
    const data = await getJSON(user_url);
    console.debug('Fetched User Data', data);
    const { user } = data;
    dispatch({
      type: actions.SET_USER, user, logout_url: data.logout_url, token: data.token,
    });
    dispatch({
      type: actions.SET_LOADED
    });
    return Promise.resolve(data);
  } catch (error) {
    return Promise.reject(error);
  }
}

async function loadUser(dispatch, user, logout_url, token) {
  dispatch({
    type: actions.SET_USER, user, logout_url, token,
  });
}

export {
  getJSON, postJSON, getUserData, loadUser, fetchToken,
};