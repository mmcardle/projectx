import React from 'react';
import { useState } from 'react';

import {
  Alert,
  Breadcrumb, Badge, Button, ButtonGroup,
  Card, Col, CardDeck, Container, Dropdown, DropdownButton,
  Form, InputGroup, FormControl, ListGroup,
  Modal, ProgressBar, Table, Tabs, Tab
} from 'react-bootstrap';

function Example() {

  const [show_modal, setShowModal] = useState(false);

  const handleCloseModal = () => setShowModal(false);
  const handleShowModal = () => setShowModal(true);

  const alerts = [
    'primary',
    'secondary',
    'success',
    'danger',
    'warning',
    'info',
    'light',
    'dark',
  ].map((variant, idx) => (
    <Alert key={idx} variant={variant}>
      This is a {variant} alert—check it out!
    </Alert>
  ));

  const badges = [
    'primary',
    'secondary',
    'success',
    'danger',
    'warning',
    'info',
    'light',
    'dark',
  ].map((variant, idx) => (
    <Badge className="mr-1" key={idx} variant={variant}>{variant}</Badge>
  ));

  const buttons = [
    'primary',
    'secondary',
    'success',
    'danger',
    'warning',
    'info',
    'light',
    'dark',
    'link'
  ].map((variant, idx) => (
    <Button className="mr-1" key={idx} variant={variant}>{variant}</Button>
  ));

   const dropdowns = [
     'primary',
     'secondary',
     'success',
     'info',
     'warning',
     'danger',
     'dark',
     'link',
    ].map(
     (variant) => (
       <DropdownButton
         as={ButtonGroup}
         key={variant}
         id={`dropdown-variants-${variant}`}
         variant={variant.toLowerCase()}
         title={variant}
         className="mr-1"
       >
         <Dropdown.Item eventKey="1">Action</Dropdown.Item>
         <Dropdown.Item eventKey="2">Another action</Dropdown.Item>
         <Dropdown.Item eventKey="3" active>
           Active Item
         </Dropdown.Item>
         <Dropdown.Divider />
         <Dropdown.Item eventKey="4">Separated link</Dropdown.Item>
       </DropdownButton>
     ),
  )

  return (
    <Container>
      <Container>
        
        <h2 className="mt-3">Breadcrumb</h2>
        <Breadcrumb>
          <Breadcrumb.Item href="#">Home</Breadcrumb.Item>
          <Breadcrumb.Item href="#">Library</Breadcrumb.Item>
          <Breadcrumb.Item active>Data</Breadcrumb.Item>
        </Breadcrumb>
        <h2 className="mt-5">Headings</h2>
        <h1 className="display-1">Display 1</h1>
        <h1 className="display-2">Display 2</h1>
        <h1 className="display-3">Display 3</h1>
        <h1 className="display-4">Display 4</h1>

        <p className="h1">h1. Bootstrap heading</p>
        <p className="h2">h2. Bootstrap heading</p>
        <p className="h3">h3. Bootstrap heading</p>
        <p className="h4">h4. Bootstrap heading</p>
        <p className="h5">h5. Bootstrap heading</p>
        <p className="h6">h6. Bootstrap heading</p>
        <h3 className="mt-5">
          Fancy display heading
          <small className="text-muted">With faded secondary text</small>
        </h3>
        <p>You can use the mark tag to <mark>highlight</mark> text.</p>
        <p><del>This line of text is meant to be treated as deleted text.</del></p>
        <p><s>This line of text is meant to be treated as no longer accurate.</s></p>
        <p><ins>This line of text is meant to be treated as an addition to the document.</ins></p>
        <p><u>This line of text will render as underlined</u></p>
        <p><small>This line of text is meant to be treated as fine print.</small></p>
        <p><strong>This line rendered as bold text.</strong></p>
        <p><em>This line rendered as italicized text.</em></p>
        <h2 className="mt-5">Buttons</h2>
        {buttons}
        <h3 className="mt-5">Button Groups</h3>
        <ButtonGroup aria-label="Basic example">
          <Button variant="secondary">Left</Button>
          <Button variant="secondary">Middle</Button>
          <Button variant="secondary">Right</Button>
        </ButtonGroup>
        <h3 className="mt-5">Dropdowns</h3>
        {dropdowns}
        <h2 className="mt-5">Badges</h2>
        {badges}
        <h2 className="mt-5">Alerts</h2>
        {alerts}
        <h2 className="mt-5">Cards</h2>
        <CardDeck>
          <Card>
            <Card.Img variant="top" src="logo.svg" className="w-50 mx-auto mt-2" />
            <Card.Body>
              <Card.Title>Card title</Card.Title>
              <Card.Text>
                This is a wider card with supporting text below as a natural lead-in to
                additional content. This content is a little bit longer.
              </Card.Text>
            </Card.Body>
            <Card.Footer>
              <small className="text-muted">Last updated 3 mins ago</small>
            </Card.Footer>
          </Card>
          <Card>
            <Card.Img variant="top" src="logo.svg" className="w-50 mx-auto mt-2" />
            <Card.Body>
              <Card.Title>Card title</Card.Title>
              <Card.Text>
                This card has supporting text below as a natural lead-in to additional
                content.{' '}
              </Card.Text>
            </Card.Body>
            <Card.Footer>
              <small className="text-muted">Last updated 3 mins ago</small>
            </Card.Footer>
          </Card>
          <Card>
            <Card.Img variant="top" src="logo.svg" className="w-50 mx-auto mt-2" />
            <Card.Body>
              <Card.Title>Card title</Card.Title>
              <Card.Text>
                This is a wider card with supporting text below as a natural lead-in to
                additional content. This card has even longer content than the first to
                show that equal height action.
              </Card.Text>
            </Card.Body>
            <Card.Footer>
              <small className="text-muted">Last updated 3 mins ago</small>
            </Card.Footer>
          </Card>
        </CardDeck>
        <h2 className="mt-5">Table</h2>
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>#</th>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Username</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>Mark</td>
              <td>Otto</td>
              <td>@mdo</td>
            </tr>
            <tr>
              <td>2</td>
              <td>Jacob</td>
              <td>Thornton</td>
              <td>@fat</td>
            </tr>
            <tr>
              <td>3</td>
              <td colSpan="2">Larry the Bird</td>
              <td>@twitter</td>
            </tr>
          </tbody>
        </Table>
        <Table striped bordered hover variant="dark">
          <thead>
            <tr>
              <th>#</th>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Username</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>Mark</td>
              <td>Otto</td>
              <td>@mdo</td>
            </tr>
            <tr>
              <td>2</td>
              <td>Jacob</td>
              <td>Thornton</td>
              <td>@fat</td>
            </tr>
            <tr>
              <td>3</td>
              <td colSpan="2">Larry the Bird</td>
              <td>@twitter</td>
            </tr>
          </tbody>
        </Table>
        <h2 className="mt-5">Tabs</h2>
        <Tabs defaultActiveKey="profile" id="uncontrolled-tab-example">
          <Tab eventKey="home" title="Home">
            <p className="m-3">Some other text in Tab Home</p>
          </Tab>
          <Tab eventKey="profile" title="Profile">
            <p className="m-3">Some text in Tab Profile</p>
          </Tab>
          <Tab eventKey="contact" title="Contact" disabled>
            <p className="m-3">Cannot see this disabled text</p>
          </Tab>
        </Tabs>
        <h2 className="mt-5">Form</h2>
        <Form>
          <Form.Row>
            <Form.Group as={Col} controlId="formGridEmail">
              <Form.Label>Email</Form.Label>
              <Form.Control type="email" placeholder="Enter email" />
            </Form.Group>

            <Form.Group as={Col} controlId="formGridPassword">
              <Form.Label>Password</Form.Label>
              <Form.Control type="password" placeholder="Password" />
            </Form.Group>
          </Form.Row>

          <Form.Group controlId="formGridAddress1">
            <Form.Label>Address</Form.Label>
            <Form.Control placeholder="1234 Main St" />
          </Form.Group>

          <Form.Group controlId="formGridAddress2">
            <Form.Label>Address 2</Form.Label>
            <Form.Control placeholder="Apartment, studio, or floor" />
          </Form.Group>

          <Form.Row>
            <Form.Group as={Col} controlId="formGridCity">
              <Form.Label>City</Form.Label>
              <Form.Control />
            </Form.Group>

            <Form.Group as={Col} controlId="formGridState">
              <Form.Label>State</Form.Label>
              <Form.Control as="select" defaultValue="Choose...">
                <option>Choose...</option>
                <option>...</option>
              </Form.Control>
            </Form.Group>

            <Form.Group as={Col} controlId="formGridZip">
              <Form.Label>Zip</Form.Label>
              <Form.Control />
            </Form.Group>
          </Form.Row>

          <Form.Group id="formGridCheckbox">
            <Form.Check type="checkbox" label="Check me out" />
          </Form.Group>

          <Button variant="primary" type="submit">
            Submit
          </Button>
        </Form>
        <h2 className="mt-5">Input Group</h2>
        <div>
          <InputGroup className="mb-3">
            <InputGroup.Prepend>
              <InputGroup.Text id="basic-addon1">@</InputGroup.Text>
            </InputGroup.Prepend>
            <FormControl
              placeholder="Username"
              aria-label="Username"
              aria-describedby="basic-addon1"
            />
          </InputGroup>

          <InputGroup className="mb-3">
            <FormControl
              placeholder="Recipient's username"
              aria-label="Recipient's username"
              aria-describedby="basic-addon2"
            />
            <InputGroup.Append>
              <InputGroup.Text id="basic-addon2">@example.com</InputGroup.Text>
            </InputGroup.Append>
          </InputGroup>

          <label htmlFor="basic-url">Your vanity URL</label>
          <InputGroup className="mb-3">
            <InputGroup.Prepend>
              <InputGroup.Text id="basic-addon3">
                https://example.com/users/
              </InputGroup.Text>
            </InputGroup.Prepend>
            <FormControl id="basic-url" aria-describedby="basic-addon3" />
          </InputGroup>

          <InputGroup className="mb-3">
            <InputGroup.Prepend>
              <InputGroup.Text>$</InputGroup.Text>
            </InputGroup.Prepend>
            <FormControl aria-label="Amount (to the nearest dollar)" />
            <InputGroup.Append>
              <InputGroup.Text>.00</InputGroup.Text>
            </InputGroup.Append>
          </InputGroup>

          <InputGroup>
            <InputGroup.Prepend>
              <InputGroup.Text>With textarea</InputGroup.Text>
            </InputGroup.Prepend>
            <FormControl as="textarea" aria-label="With textarea" />
          </InputGroup>
        </div>
        <h2 className="mt-5">List Group</h2>
        <ListGroup>
          <ListGroup.Item active>Cras justo odio</ListGroup.Item>
          <ListGroup.Item>Dapibus ac facilisis in</ListGroup.Item>
          <ListGroup.Item>Morbi leo risus</ListGroup.Item>
          <ListGroup.Item>Porta ac consectetur ac</ListGroup.Item>
          <ListGroup.Item disabled>Vestibulum at eros</ListGroup.Item>
        </ListGroup>
        <ListGroup className="mt-4">
          <ListGroup.Item>No style</ListGroup.Item>
          <ListGroup.Item variant="primary">Primary</ListGroup.Item>
          <ListGroup.Item variant="secondary">Secondary</ListGroup.Item>
          <ListGroup.Item variant="success">Success</ListGroup.Item>
          <ListGroup.Item variant="danger">Danger</ListGroup.Item>
          <ListGroup.Item variant="warning">Warning</ListGroup.Item>
          <ListGroup.Item variant="info">Info</ListGroup.Item>
          <ListGroup.Item variant="light">Light</ListGroup.Item>
          <ListGroup.Item variant="dark">Dark</ListGroup.Item>
        </ListGroup>
        <h2 className="mt-5">Modals</h2>
        <Modal.Dialog>
          <Modal.Header closeButton>
            <Modal.Title>Modal title</Modal.Title>
          </Modal.Header>

          <Modal.Body>
            <p>Modal body text goes here.</p>
          </Modal.Body>

          <Modal.Footer>
            <Button variant="secondary">Close</Button>
            <Button variant="primary">Save changes</Button>
          </Modal.Footer>
        </Modal.Dialog>

        <Button variant="primary" onClick={handleShowModal}>
          Launch demo modal
        </Button>

        <Modal show={show_modal} onHide={handleCloseModal}>
          <Modal.Header closeButton>
            <Modal.Title>Modal heading</Modal.Title>
          </Modal.Header>
          <Modal.Body>Woohoo, you're reading this text in a modal!</Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
              Close
            </Button>
            <Button variant="primary" onClick={handleShowModal}>
              Save Changes
            </Button>
          </Modal.Footer>
        </Modal>

        <h2 className="mt-5">Progress</h2>
        <div>
          <ProgressBar striped variant="success" now={40} />
          <ProgressBar striped variant="info" now={20} />
          <ProgressBar striped variant="warning" now={60} />
          <ProgressBar striped variant="danger" now={80} />
        </div>

      </Container>
    </Container>
  );
}

export default Example;
