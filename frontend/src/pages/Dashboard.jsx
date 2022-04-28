import React from 'react';
import { withNamedStores } from '../store/state';
import PropTypes from 'prop-types';

function Dashboard(props) {
  return (
    <div className="p-4 m-auto text-center">
      <img className="w-50" src="/static/img/logo.svg" alt="Logo" />
      <div className="display-3">
        Welcome {props.user.display_name}
      </div>
    </div>
  );
}

Dashboard.propTypes = {
  user: PropTypes.shape({
    display_name: PropTypes.string.isRequired,
  })
}

export default withNamedStores(Dashboard, ['user']);