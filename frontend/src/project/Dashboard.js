import React from 'react';
import { withNamedStores } from '../store/state';

function Dashboard(props) {
  return (
    <div className="p-4">
      <img src="logo.svg" className="p-2 w-25 h-50 m-auto" alt="Logo" />
      <div className="display-3">
        Welcome {props.user.display_name}
      </div>
    </div>
  );
}

export default withNamedStores(Dashboard, ['user']);