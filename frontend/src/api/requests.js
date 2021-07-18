
import axios from 'axios';

import actions from '../store/actions';
import {
  user_url, login_url, activate_url, forgot_password_url,
  register_url, reset_password_check_url, reset_password_complete_url,
  change_password_url, change_details_url, open_api_url,
} from './urls';

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

async function deleteJSON(url, args = {}) {
  const request_args = args;
  request_args.transformResponse = (data) => {
    console.debug(url, data);
    // Ensure data is valid json
    return JSON.parse(data);
  };
  const response = await axios.delete(url, request_args);
  console.debug('DELETE to', url, request_args, ':', response.data);
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

async function patchJSON(url, params, args = {}) {
  const request_args = args;
  request_args.transformResponse = (data) => {
    console.debug(url, data);
    // Ensure data is valid json
    return JSON.parse(data);
  };
  const response = await axios.patch(url, params, request_args);
  console.debug('PATCH to', url, request_args, ':', response.data);
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
    const open_api_data = await getJSON(open_api_url);
    dispatch({type: actions.SET_OPENAPI, open_api_data});
    const user_data = await getJSON(user_url);
    console.debug('Fetched User Data', user_data);
    const { user } = user_data;
    if (user) {
      dispatch({
        type: actions.SET_USER, user, logout_url: user_data.logout_url, token: user_data.token, jwt: user_data.jwt
      });
    } else {
      dispatch({type: actions.SET_LOADED});
      return Promise.resolve();
    }
    return Promise.resolve(user_data);
  } catch (error) {
    dispatch({type: actions.SET_LOADED});
    return Promise.resolve(error);
  }
}

async function logout(dispatch, logout_url) {
  try {
    const token = await fetchToken(user_url);
    await postJSON(logout_url, {}, { headers: { 'X-CSRFToken': token } });
    dispatch({ type: actions.SET_LOGGED_OUT });
    return Promise.resolve();
  } catch (error) {
    console.log('Could not log out', error);
    return Promise.reject(error);
  }
}

async function login(dispatch, email, password) {
  try {
    const token = await fetchToken(user_url);
    const data = await postJSON(login_url, { email, password }, { headers: { 'X-CSRFToken': token } })
    loadUser(dispatch, data.user, data.logout_url, data.token, data.jwt)
    return Promise.resolve(data);
  } catch (error) {
    console.log('Could not log in', error);
    return Promise.reject(error);
  }
}

async function activate(activate_key) {
  try {
    const token = await fetchToken(user_url);
    const data = await postJSON(
      activate_url, {activate_key}, { headers: { 'X-CSRFToken': token } },
    )
    return Promise.resolve(data);
  } catch (error) {
    console.log('Could not activate', error);
    return Promise.reject(error);
  }
}

async function forgotPassword(email) {
  try {
    const token = await fetchToken(user_url);
    const data = await postJSON(
      forgot_password_url, { email }, { headers: { 'X-CSRFToken': token } },
    )
    return Promise.resolve(data);
  } catch (error) {
    console.log('Could not forget password', error);
    return Promise.reject(error);
  }
}

async function resetPasswordCheck(reset_key) {
  try {
    const token = await fetchToken(user_url);
    const data = await postJSON(
      reset_password_check_url, { reset_key }, { headers: { 'X-CSRFToken': token } },
    )
    return Promise.resolve(data);
  } catch (error) {
    console.log('Could not check reset key', error);
    return Promise.reject(error);
  }
}

async function resetPasswordComplete(reset_key, password1, password2) {
  try {
    const token = await fetchToken(user_url);
    const data = await postJSON(
      reset_password_complete_url,
      { reset_key, password1, password2 },
      { headers: { 'X-CSRFToken': token } },
    )
    return Promise.resolve(data);
  } catch (error) {
    console.log('Could not reset passowrd', error);
    return Promise.reject(error);
  }
}

async function register(email, password1, password2, first_name, last_name) {
  try {
    const token = await fetchToken(user_url);
    const data = await postJSON(
      register_url,
      { email, password1, password2, first_name, last_name },
      { headers: { 'X-CSRFToken': token } },
    )
    return Promise.resolve(data);
  } catch (error) {
    console.log('Could not register', error);
    return Promise.reject(error);
  }
}

async function changePassword(current_password, password1, password2) {
  try {
    const token = await fetchToken(user_url);
    const data = await postJSON(
      change_password_url,
      { current_password, password1, password2 },
      { headers: { 'X-CSRFToken': token } },
    )
    return Promise.resolve(data);
  } catch (error) {
    console.log('Could not change password', error);
    return Promise.reject(error);
  }
}


async function changeDetails(first_name, last_name) {
  try {
    const token = await fetchToken(user_url);
    const data = await postJSON(
      change_details_url,
      { first_name, last_name },
      { headers: { 'X-CSRFToken': token } },
    )
    return Promise.resolve(data);
  } catch (error) {
    console.log('Could not change details', error);
    return Promise.reject(error);
  }
}

async function loadUser(dispatch, user, logout_url, token, jwt) {
  dispatch({type: actions.SET_USER, user, logout_url, token, jwt});
}

export {
  getJSON, postJSON, patchJSON, getUserData, loadUser, fetchToken, login, logout,
  activate, forgotPassword, resetPasswordCheck, resetPasswordComplete,
  register, changePassword, changeDetails, deleteJSON,
};