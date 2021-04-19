import React from 'react';
import PropTypes from 'prop-types';

import { Container, Row, Col } from 'react-bootstrap';
import Card from 'react-bootstrap/Card';

function CentralContainer(props) {
  return (
    <div className="central-container">
        <div className="central-item">
          <Container fluid >
            <Row noGutters className="justify-content-center">
              <Col xs={12} sm={10} md={6} lg={6} xl={4} style={{maxWidth: "400px"}}>
                <Card bg="transparent" border="none" className="central-card">
                  <Card.Img variant="top" src="/logo.svg" className="p-2 m-auto" style={{width: "200px"}} />
                  <Card.Body>
                    <Card.Title className="text-center display-3">{process.env.REACT_APP_PROJECT_TITLE}</Card.Title>
                    {props.children}
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Container>
        </div>
    </div>
  );
}

CentralContainer.propTypes = {
  children: PropTypes.arrayOf(PropTypes.node).isRequired
}

export default CentralContainer;
