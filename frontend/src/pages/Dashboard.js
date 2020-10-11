import React from 'react';
import { withNamedStores } from '../store/state';

function Dashboard(props) {
  return (
    <div>
      <h2>Dashboard {props.user.display_name}</h2>
    </div>
  );
}

export default withNamedStores(Dashboard, ['user']);