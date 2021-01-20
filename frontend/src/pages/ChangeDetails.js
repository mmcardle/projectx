import React, { useState } from 'react';
import PropTypes from 'prop-types';

import { withNamedStores } from '../store/state';
import { changeDetails } from '../api/requests';

import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

function ChangeDetails(props) {

  console.debug('ChangeDetails', props)

  const [first_name, setFirstName] = useState(props.user.first_name)
  const [last_name, setLastName] = useState(props.user.last_name)
  const [complete, setComplete] = useState(false)
  const [error, setError] = useState(undefined)
  const [errors, setErrors] = useState({})

  function click(e) {
    e.preventDefault()
    setError(undefined);
    setErrors({});
    changeDetails(first_name, last_name).then(() => {
      setComplete(true);
    }).catch(error => {
      if (error.response && error.response.data && error.response.data.errors) {
        setErrors(error.response.data.errors);
      }
      setError(`Sorry we couldn't change your details at this time.`);
    })
  }

  return (
    <Form onSubmit={click} className="d-flex flex-column h-100">
      <h3>Change Details</h3>
      { complete ? <Alert variant="success">Details have been updated.</Alert> : <></> }
      { error ? <Alert variant="danger">{error}</Alert> : <></> }
      <Form.Group controlId="first_name">
        <Form.Label>First Name</Form.Label>
        { errors.first_name ? <Alert variant="danger">{errors.first_name}</Alert> : <></> }
        <Form.Control required type="text" placeholder="First Name" value={first_name} onChange={e => setFirstName(e.target.value)} />
      </Form.Group>
      <Form.Group controlId="last_name">
        <Form.Label>Last Name</Form.Label>
        { errors.last_name ? <Alert variant="danger">{ errors.last_name }</Alert> : <></> }
        <Form.Control required type="text" placeholder="Last Name" value={last_name} onChange={e => setLastName(e.target.value)} />
      </Form.Group>
      <Button block variant="primary" type="submit" className="mt-auto">
        Update
      </Button>
    </Form>
  );
}

ChangeDetails.propTypes = {
  user: PropTypes.shape({
    first_name: PropTypes.string.isRequired,
    last_name: PropTypes.string.isRequired,
  })
}

export default withNamedStores(ChangeDetails, ['user']);