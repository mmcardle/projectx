import React from 'react';
import { Link } from "react-router-dom";

import CentralContainer from '../containers/CentralContainer'

import Alert from 'react-bootstrap/Alert';
import Card from 'react-bootstrap/Card';

function NotFound(props) {
  return (
    <CentralContainer>
      <Card bg="dark" text="white" border="secondary" style={{ width: '25rem' }} >
        <Card.Img variant="top" src="../logo.svg" className="p-2 w-50 m-auto" />
        <Card.Body>
          <Card.Title className="text-center display-3">Project X</Card.Title>
          <Card.Body>
            <Alert variant="info">
              Sorry we could not find that page.
            </Alert>
            <div className="text-center">
              <Link to="/">To the Home Page</Link>
            </div>
          </Card.Body>
        </Card.Body>
      </Card>
    </CentralContainer>
  );
}

export default NotFound;
