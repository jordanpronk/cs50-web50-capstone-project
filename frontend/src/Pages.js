import React, { useEffect } from "react";
import DeckList from "./components/DeckList";
import Login from "./components/Login"
import Deck from './components/Deck'
import { Row, Col } from "react-bootstrap";

import {
    Switch,
    Route,
  } from "react-router-dom";
import Register from "./components/Register";
import { doFetchPost } from "./FetchHelper";

export function LoginPage({handleUserLogin}) {
    return (
        <div>
            <h1>Login</h1>
            <Row>
                <Col md={0} lg={4}></Col>
                <Col>
                    <Login handleUserLogin={handleUserLogin}/>
                </Col>
                <Col md={0} lg={4}></Col>
            </Row>
        </div>
    );
}

export function LogoutPage({loginUser, handleUserLogin}) {

    useEffect(function() {
        doFetchPost("/user/logout")
        .then(response=>response.json())
        .then(result=>{
            handleUserLogin();
        })
        .catch(console.error);
    },[]);

    return (
        <div>
            <h1>Log Out</h1>
            <p>You have successfully logged out</p>
        </div>
    );
}


export function RegisterPage({handleUserLogin}) {
    return (
        <div>
            <h1>Register</h1>
            <Row>
                <Col md={0} lg={4}></Col>
                <Col>
                    <Register handleUserLogin={handleUserLogin}/>
                </Col>
                <Col md={0} lg={4}></Col>
            </Row>
        </div>
    );
}

export function DecksPage({loggedInUser}) {
    return (
        <div className="justify-content-center">
        <Switch>
            <Route exact path="/decks">
                <Row>
                <Col >
                    <h1>Decks</h1>
                </Col>
                </Row>
                <Row>
                <Col>
                    <DeckList key={0} subscribedOnly={false} loggedInUser={loggedInUser}/>
                </Col>
                </Row>
            </Route>
            <Route exact path="/decks/subscribed">
                <Row>
                <Col >
                    <h1>Subscribed Decks</h1>
                </Col>
                </Row>
                <Row>
                <Col>
                    <DeckList key={1} subscribedOnly={true} loggedInUser={loggedInUser}/>
                </Col>
                </Row>
                
            </Route>
            <Route exact path="/decks/:deck_id">
                <Row>
                <Col >
                    <Deck loggedInUser={loggedInUser}/>
                </Col>
                </Row>
            </Route>
            <Route path="*">
                <NotFound404 />
            </Route>
        </Switch>
        </div>
    );
}

export function ReviewPage() {
    return (
        <div>
            <h1>Review</h1>
        </div>
    );
}

export function NotFound404() {
    return (
        <div>
            <h1>404</h1>
            <h2> Not found </h2>
        </div>
    );
}