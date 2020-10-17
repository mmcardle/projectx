import React from 'react';
import { withNamedStores } from '../store/state';

function Dashboard(props) {
  return (
    <div className="main-content-item text-center mt-5">
      <div className="bg-dark w-50 mx-auto rounded border border-secondary p-4 text-white">
        <img src="logo.svg" className="p-2 w-25 h-50 m-auto" alt="ProjectX logo" />
        <div className="display-3">
          Welcome {props.user.display_name}
        </div>
        <div className="display-4">
          Email: {props.user.email}
        </div>
      </div>
    </div>
  );
}

export default withNamedStores(Dashboard, ['user']);