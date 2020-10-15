
const create_websocket = () => {
  const wsprotocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
  const ws_url = `${wsprotocol + window.location.hostname}:${window.location.port}/ws/`;
  return new WebSocket(ws_url);
};

const setup_websocket = (ws, dispatch) => {
  const websocket = ws;

  websocket.onopen = () => {
    // Web Socket is connected
  };

  websocket.onmessage = (evt) => {
    const msg = evt.data;
    const jsonMsg = JSON.parse(msg);
    if (jsonMsg.SOME_MESSAGE) {
      //dispatch({ type: actions.SET_USER, payload: jsonMsg });
    } else {
      console.debug('Unknown message', jsonMsg);
    }
  };

  websocket.onclose = () => {
    // websocket is closed.
  };
};


export { create_websocket, setup_websocket };