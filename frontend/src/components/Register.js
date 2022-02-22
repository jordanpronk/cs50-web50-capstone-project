import React from "react";
import { useState } from 'react';
import { Alert, Form, Button } from "react-bootstrap";
import { doFetchPost } from "../FetchHelper";

export default function Register({handleUserLogin}) {

    const [username,setUsername]=useState("");
    const [email,setEmail]=useState("");
    const [password,setPassword]=useState("");
    const [passwordConfirm,setPasswordConfirm]=useState("");
    const [errorMessage,setErrorMessage]=useState(undefined);

    function handleEmailChange(e) {
        setEmail(e.target.value);
    }

    function handlePasswordChange(e) {
        setPassword(e.target.value);
    }

    function handlePasswordConfirmChange(e) {
        setPasswordConfirm(e.target.value);
    }

    function handleUsernameChange(e) {
        setUsername(e.target.value);
    }

   function handleLogin() {
        doFetchPost("/user/register", {username: username, email: email, password: password, confirmation: passwordConfirm})
        .then(response => response.json())
        .then(result => {
            if(result.error) {
                setErrorMessage(result.error);
            } else {
                setErrorMessage(undefined);
                if(result.logged_in === true) {
                    handleUserLogin({user_id: result.user_id, username: result.username, authenticated: result.logged_in});
                }
            }
        })
        .catch((error)=>console.error(error));
        
   }

    return(
        <div>
            {errorMessage ? <Alert variant="danger">{errorMessage}</Alert> : <></>}

            <Form>
                <Form.Group className="mb-3">
                    <Form.Control className="my-4" type="text" placeholder="Enter username" onChange={handleUsernameChange} value={username}/>
                    <Form.Control className="mb-4" type="email" placeholder="Enter email" onChange={handleEmailChange} value={email}/>
                    <Form.Control className="mb-4" type="password" placeholder="Enter password" onChange={handlePasswordChange} value={password}/>
                    <Form.Control className="mb-4" type="password" placeholder="Confirm password" onChange={handlePasswordConfirmChange} value={passwordConfirm}/>
                </Form.Group>
                <Button className="my-3" variant="primary" onClick={handleLogin}>Register</Button>
              </Form>
        </div>
    );
}