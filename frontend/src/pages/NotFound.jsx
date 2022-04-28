import React from 'react';
import { Link } from "react-router-dom";

import CentralContainer from '../containers/CentralContainer'

import Alert from 'react-bootstrap/Alert';

function NotFound() {
  return (
    <CentralContainer>
      <Alert variant="info">
        Sorry we could not find that page.
      </Alert>
      <div className="text-center">
        <Link to="/">To the Home Page</Link>
      </div>
    </CentralContainer>
  );
}

export default NotFound;
