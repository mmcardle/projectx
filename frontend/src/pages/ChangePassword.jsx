import React, { useState } from 'react';

import { changePassword } from '../api/requests';

import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

function ChangePassword() {

  const [current_password, setCurrentPassword] = useState("")
  const [password1, setPassword1] = useState("")
  const [password2, setPassword2] = useState("")
  const [complete, setComplete] = useState(false)
  const [error, setError] = useState(undefined)
  const [errors, setErrors] = useState({})

  function click(e) {
    setError(undefined);
    setErrors({});
    e.preventDefault()

    changePassword(current_password, password1, password2)
    .then(() => {
      setComplete(true);
      setCurrentPassword("")
      setPassword1("")
      setPassword2("")
    })
    .catch(error => {
      if (error.response && error.response.data && error.response.data.errors) {
        setErrors(error.response.data.errors);
      }
      setError(`Sorry we couldn't change your password at this time.`);
    })
  }

  return (
    <Form onSubmit={click} className="d-flex flex-column h-100 p-3 border rounded">
      <h3>Change Password</h3>
      { complete ? <Alert variant="success">Password has been updated.</Alert> : <></> }
      { error ? <Alert variant="danger">{error}</Alert> : <></> }
      <Form.Group controlId="currentPassword">
        <Form.Label>Current Password</Form.Label>
        { errors.current_password ? <Alert variant="danger">{errors.current_password}</Alert> : <></> }
        <Form.Control required type="password" placeholder="Password" value={current_password} onChange={e => setCurrentPassword(e.target.value)} />
      </Form.Group>
      <Form.Group controlId="changePassword1">
        <Form.Label>Set New Password</Form.Label>
        { errors.password1 ? <Alert variant="danger">{ errors.password1 }</Alert> : <></> }
        <Form.Control required type="password" placeholder="New Password" value={password1} onChange={e => setPassword1(e.target.value)} />
      </Form.Group>
      <Form.Group controlId="changePassword2">
        <Form.Label className="d-none sr-block">New Password Again</Form.Label>
        {  errors.password2 ? <Alert variant="danger">{ errors.password2 }</Alert> : <></> }
        <Form.Control required type="password" placeholder="New Password Again" value={password2} onChange={e => setPassword2(e.target.value)} />
      </Form.Group>
      <Button block variant="primary" type="submit" className="mt-auto">
        Update
      </Button>
    </Form>
  );
} 

export default ChangePassword;