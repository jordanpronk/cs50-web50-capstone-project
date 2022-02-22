import './App.css';

import { useEffect, useState } from 'react';
import NavHeader from './components/NavHeader'
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect
} from "react-router-dom";
import { LoginPage, LogoutPage, DecksPage, NotFound404, RegisterPage } from './Pages'
import { doFetch } from './FetchHelper';
import { Container } from 'react-bootstrap';

function App() {

  const defaultLoggedOutUser = {userId: undefined, username: undefined, loggedIn: false};
  const [loginUser,setLoginUser]=useState(defaultLoggedOutUser);

  function handleUserLogin() {
    getUserLoginStatus();
  }

  function getUserLoginStatus(){
    doFetch("/user", {})
    .then(response => response.json())
    .then(result => {
        if(result.logged_in){
            setLoginUser({userId: result.user.id, username: result.user.username, loggedIn: result.logged_in});
        } else {
          setLoginUser(defaultLoggedOutUser);
        }
    })
    .catch(console.error);
  }

  useEffect( function() {
    getUserLoginStatus()
  },[]);

  return (
    <Router>
      <div>
        <NavHeader loginUser={loginUser} />
      </div>
      <Container fluid="md" className="text-center">
      <Switch>
        <Route exact path="/login">
          {loginUser.loggedIn ? <Redirect to="/" /> : <LoginPage handleUserLogin={handleUserLogin}/>}
        </Route>
        <Route exact path="/logout">
          <LogoutPage loginUser={loginUser} handleUserLogin={handleUserLogin}/>
        </Route>
        <Route exact path="/register">
          {loginUser.loggedIn ? <Redirect to="/decks" /> : <RegisterPage handleUserLogin={handleUserLogin}/>}
        </Route>
        <Route path="/decks">
          {!loginUser.loggedIn ? <Redirect to="/login" /> : <DecksPage loggedInUser={loginUser} />}
        </Route>
        <Route exact path="/">
          <Redirect to="/decks" />
        </Route>
        <Route path="*">
          <NotFound404 />
        </Route>
      </Switch>
      </Container>
    </Router>
  );
}

export default App;
