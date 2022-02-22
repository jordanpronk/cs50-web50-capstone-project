import { Button, Col, ButtonGroup, Alert, ProgressBar} from 'react-bootstrap';
import React from 'react'
import { useEffect, useState } from 'react';
import Flashcard from './Flashcard';

import { Modal, Badge } from 'react-bootstrap';
import { doFetchPost } from '../FetchHelper';

export function ReviewModal({deck_id, selectedCard, numNew, numDue, numEarly, onGetDeckReview}) {

  const [show, setShow] = useState(false);
  const [showFront, setShowFront] = useState(true);

  function handleClose() {
    setShow(false);
  }

  function getNumTotal() {
    return 0.0 + numNew + numDue + numEarly
  }

  function isFinishedDeckReview() {
    return numNew === 0 && numDue === 0;
  }

  function handleOpen() {
    setShow(true);
  }

  function pickRandomCard() {
    onGetDeckReview();
    setShowFront(true);
  }

  function handleReviewed(difficultyScore, cardId) {
    doFetchPost(`/decks/${deck_id}/review`, { 
      card_id: cardId,
      difficulty: difficultyScore})
    .then(response=>response.json())
    .then(result=>{
      pickRandomCard();
    })
    .catch(e=>{
      console.error(e);
    });
  }

  function flipCard() {
    if(!selectedCard) {
      return;
    }
    setShowFront(false);
  }

  useEffect(function(){
    if(show){
      pickRandomCard()
    }
  },[show])

  if (show) {
    return (
      <Modal show={show} fullscreen={true} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>Review</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="flashcard-modal-body"> 
          <ProgressBar>
            <ProgressBar variant="success" now={getNumTotal() > 0 ? numEarly/getNumTotal()*100.0 : 100} key={1} label={`${numEarly} done`}/>
            <ProgressBar variant="danger" now={getNumTotal() > 0 ? numDue/getNumTotal()*100.0 : 0} key={2} label={`${numDue} due`}/>
            <ProgressBar variant="warning" now={getNumTotal() > 0 ? numNew/getNumTotal()*100.0 : 0} key={3} label={`${numNew} new`}/>
          </ProgressBar>
          {
            isFinishedDeckReview() ?
              <Alert variant="success">
                You've finished reviewing all cards in this deck!
              </Alert>
              :
              <></>
          }
          {
            selectedCard ? 
              <Flashcard showFront={showFront} front={selectedCard.front_content} back={selectedCard.back_content} /> 
            : 
              <div>No Cards to Review</div> 
          }
          </div>
        </Modal.Body>
        <Modal.Footer className="mx-0">
          {
            showFront ? 
              <Button as={Col} size="lg" variant="dark" className="review-button-footer" onClick={flipCard}>Show</Button> 
            : 
              <ButtonGroup as={Col} size="lg" className="gap-2">
                <Button variant="dark" className="review-button-footer" onClick={()=>handleReviewed(1, selectedCard.id)}>Easy</Button>
                <Button variant="dark" className="review-button-footer" onClick={()=>handleReviewed(3, selectedCard.id)}>Normal</Button>
                <Button variant="dark" className="review-button-footer" onClick={()=>handleReviewed(5, selectedCard.id)}>Hard</Button>
              </ButtonGroup>
          }
        </Modal.Footer>
      </Modal>
    )
  } else {
    return (
      <Button variant="primary" onClick={handleOpen}>Review { numDue > 0 ? <Badge bg="secondary">{numDue}</Badge> : <></>} </Button>
    )
  }
}
