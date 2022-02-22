import React from 'react'
import { useState } from 'react';
import { useParams } from 'react-router';

import { Modal, Button, Form } from 'react-bootstrap';
import { doFetchPost, doFetchPut, doFetchDelete } from '../FetchHelper';


function DeckFormModal({deckObj, title, onSaveDeck}) {
  /*
    mode = 'create' | 'edit'
   */
    const [editMode,setEditMode]=useState(false);
    const {deck_id} = useParams();

    const [deckName,setDeckName]=useState("");
    const [description,setDescription]=useState("");
    // /create to create a new deck
    // /:id to update an existing deck

    function handleOpen(){
      setEditMode(true);
      setDeckName(deckObj ? deckObj.name : "");
      setDescription(deckObj ? deckObj.description : "");
    }

    function handleClose() {
      setEditMode(false);
    }

    function handleDeckNameChange(e) {
        setDeckName(e.target.value);
    }

    function handleDeckDescriptionChange(e) {
      setDescription(e.target.value);
    }

    function handleCreateDeck() {
      doFetchPost("/decks",{name: deckName, description: description})
      .then(response=>response.json())
      .then(result=>{
        handleClose();
        onSaveDeck({name: deckName, action: 'create'});
      })
      .catch(console.error);
    }

    function handleUpdateDeck() {
      doFetchPut(`/decks/${deck_id}`,{name: deckName, description: description})
      .then(response=>response.json())
      .then(result=>{
        handleClose();
        onSaveDeck({name: deckName, action: 'update'});
      })
      .catch(console.error);
    }

    function handleDeleteDeck() {
      doFetchDelete(`/decks/${deck_id}`,{name: deckName, description: description})
      .then(response=>response.json())
      .then(result=>{
        handleClose();
        onSaveDeck({name: deckName, action: 'delete'});
      })
      .catch(console.error);
    }

      return (
          <div>
          <Button variant="primary" onClick={handleOpen}>{title}</Button>
          <Modal show={editMode} onHide={handleClose}>
            <Modal.Header closeButton>
              <Modal.Title>{title}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <div>
              <Form>
                  <Form.Group className="mb-3" controlId="formCreateDeck">
                      <Form.Label>Name</Form.Label>
                      <Form.Control type="text" placeholder="Enter name" onChange={handleDeckNameChange} value={deckName}/>
                      <Form.Label>Description</Form.Label>
                      <Form.Control as="textarea" placeholder="Enter Description" onChange={handleDeckDescriptionChange} value={description}/>
                  </Form.Group>
              </Form>
              </div>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={handleClose}>Close</Button>
              { deckObj ? 
                  <>
                  <Button variant="danger" onClick={handleDeleteDeck}>Delete</Button>
                  <Button variant="primary" onClick={handleUpdateDeck}>Save</Button>
                  </>
                :
                  <Button variant="primary" onClick={handleCreateDeck}>Create</Button>
              }
            </Modal.Footer>
          </Modal>
        </div>
      );
}


export default DeckFormModal;
