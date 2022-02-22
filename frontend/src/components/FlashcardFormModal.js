import React from 'react'
import { useState } from 'react';

import { useParams } from 'react-router';
import { Modal, Button } from 'react-bootstrap';
import { doFetchPost, doFetchPut, doFetchDelete } from '../FetchHelper';

function FlashcardFormModal({cardObj, title, buttonText, onSaveFlashcard}) {
    const [editMode,setEditMode]=useState(false);
    const [front,setFront]=useState("");
    const [back,setBack]=useState("");
    const {deck_id} = useParams();

    function handleCreateFlashcard() {
        doFetchPost(`/decks/${deck_id}/cards`,{front_content: front, back_content: back})
        .then(response=>response.json())
        .then(result=>{
            onSaveFlashcard(result);
            handleClose();
        })
        .catch(console.error);
            setEditMode(false);
            setFront("");
            setBack("");
    }

    function handleUpdateFlashcard() {
      doFetchPut(`/decks/${deck_id}/cards/${cardObj.id}`,{front_content: front, back_content: back})
      .then(response=>response.json())
      .then(result=>{
          onSaveFlashcard(result);
          handleClose();
      })
      .catch(console.error);
          setEditMode(false);
          setFront("");
          setBack("");
    }
    
    function handleDeleteFlashcard() {
      doFetchDelete(`/decks/${deck_id}/cards/${cardObj.id}`,{})
      .then(response=>response.json())
      .then(result=>{
          onSaveFlashcard(result);
          handleClose();
      })
      .catch(console.error);
          setEditMode(false);
          setFront("");
          setBack("");
    }

    function handleFrontChanged(e){
        setFront(e.target.value);
    }

    function handleBackChanged(e){
        setBack(e.target.value);
    }

    function handleOpen(){
      setEditMode(true);
      setFront(cardObj ? cardObj.front_content : "");
      setBack(cardObj ? cardObj.back_content : "");
    }

    function handleClose() {
      setEditMode(false);
    }
  
    return (
      <>
        <Button variant="primary" onClick={handleOpen}>{buttonText}</Button>
        <Modal show={editMode} onHide={handleClose}>
          <Modal.Header closeButton>
            <Modal.Title>{title}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div>
              <textarea placeholder="front" value={front} onChange={handleFrontChanged}></textarea>
              <textarea placeholder="back" value={back} onChange={handleBackChanged}></textarea>
              
            </div>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleClose}>Close</Button>
            {cardObj ? 
                <>
                  <Button variant="danger" onClick={handleDeleteFlashcard}>Delete</Button>
                  <Button variant="primary" onClick={handleUpdateFlashcard}>Save</Button>
                </>
              :
                <Button variant="primary" onClick={handleCreateFlashcard}>Create</Button>
            }
          </Modal.Footer>
        </Modal>
      </>
    )

}



export default FlashcardFormModal;
