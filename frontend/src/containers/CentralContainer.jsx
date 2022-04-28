import React from 'react';
import PropTypes from 'prop-types';
import { FaCog } from 'react-icons/fa';
import { Container, Row, Col } from 'react-bootstrap';
import Card from 'react-bootstrap/Card';

const title = import.meta.env.VITE_APP_PROJECT_TITLE

function CentralContainer(props) {
  return (
    <Container fluid className="mx-auto h-100">
      <Row noGutters className="justify-content-center vertical-center">
        <Col xs={12} sm={10} md={6} lg={6} xl={6} style={{maxWidth: "500px"}}>
          <Card bg="transparent" border="none" className="central-card">
            <Card.Body>
              <Card.Title className="text-center display-4">
                {title}
              </Card.Title>
              <div className="bg-danger p-2 text-white shadow-md rounded-pill mx-auto text-center mb-4 w-25 text-monospace fa-spin">Beta <FaCog /></div>
              {props.children}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

CentralContainer.propTypes = {
  children: PropTypes.arrayOf(PropTypes.node).isRequired
}

export default CentralContainer;
