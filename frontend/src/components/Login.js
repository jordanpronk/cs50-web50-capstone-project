import React from "react";
import { useState } from 'react';
import { Alert, Button, Form } from "react-bootstrap";
import { doFetchPost } from "../FetchHelper";
import { Link } from "react-router-dom";

export default function Login({handleUserLogin}) {

    const [username,setUsername]=useState("");
    const [password,setPassword]=useState("");
    const [isInvalidCredentials,setIsInvalidCredentials]=useState(false);

    function handleUsernameChange(e) {
        setUsername(e.target.value);
    }

    function handlePasswordChange(e) {
        setPassword(e.target.value);
    }

   function handleLogin() {
        doFetchPost("/user/login", {username: username, password: password})
        .then(response => response.json())
        .then(result => {
            if(!result.logged_in) {
                setIsInvalidCredentials(true);
            } else {
                setIsInvalidCredentials(false);
                handleUserLogin({user_id: result.user_id, username: result.username, authenticated: result.logged_in});
            }
        })
        .catch(console.error);
   }

    return(
        <div>
            {isInvalidCredentials ? <Alert variant="danger">Invalid Login Credentials</Alert> : <></>}
            <Form>
                <Form.Group className="mb-3">
                    <Form.Control className="my-4" type="text" placeholder="Enter username" onChange={handleUsernameChange} value={username}/>
                    <Form.Control className="mb-4" type="password" placeholder="Enter password" onChange={handlePasswordChange} value={password}/>
                </Form.Group>
                <Button className="my-3" variant="primary" onClick={handleLogin}>Login</Button>
              </Form>
              <Link   to="/register"> Register </Link>
        </div>
    );
}