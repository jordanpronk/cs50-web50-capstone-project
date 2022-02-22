import { Navbar, Container, Nav} from "react-bootstrap";
import { Link } from "react-router-dom";

export default function NavHeader({loginUser}) {
    return(
    <Navbar collapseOnSelect expand="lg" variant="dark" bg="dark" >
    <Container fluid>
      <Navbar.Brand as={Link} to="/">Memorize</Navbar.Brand>
      <Navbar.Toggle aria-controls="responsive-navbar-nav" />
        <Navbar.Collapse>
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/decks">Decks</Nav.Link>
            <Nav.Link as={Link} to="/decks/subscribed">Subscribed</Nav.Link>
          </Nav>
          <Nav>
              {
                loginUser.loggedIn ? 
                  <Nav.Link  as={Link} to="/logout"> Logout ({loginUser.username})</Nav.Link>
                :
                  <Nav.Link as={Link} to="/login">Login</Nav.Link>
              }
          </Nav>
        </Navbar.Collapse>
    </Container>
    </Navbar>
    );
}
