import React from 'react'
import { useEffect, useState } from 'react';
import { FlashcardTable } from './Flashcard'
import FlashcardFormModal from './FlashcardFormModal'
import {
    Redirect
  } from "react-router-dom";
import { useParams } from 'react-router';
import { doFetch } from '../FetchHelper';
import { ReviewModal } from './DeckReview';
import DeckFormModal from './DeckFormModal';
import { Stack, Row, Col} from 'react-bootstrap';

function Deck({loggedInUser}) {
    /*
    loggedInUser = {
        userId: <int>
        username: <str>
        loggedIn: <boolean>
    }
    */
    const {deck_id} = useParams();

    const [deckObj,setDeckObj]=useState({id: undefined, name: '', description: '', subscribers: undefined, creator_id: undefined});
    const [deckCards,setDeckCards]=useState([]);
   
    const [selectedCard, setSelectedCard] = useState();
    const [numNew, setNumNew] = useState(0)
    const [numDue, setNumDue] = useState(0)
    const [numEarly, setNumEarly] = useState(0)
    const [isDeleted, setIsDeleted] = useState(false);

    function userOwnsDeck() {
        return deckObj.creator_id === loggedInUser.userId;
    }

    function getDeckCards() {
        doFetch(`/decks/${deck_id}/cards`,{})
        .then(response=>response.json())
        .then(result=>{
            setDeckCards(result);
        })
        .catch(console.error);
    }

    function getDeckData() {
        doFetch(`/decks/${deck_id}`,{})
        .then(response=>response.json())
        .then(result=>{
            setDeckObj(result);
        })
        .catch(console.error);
    }

    function getDeckReviewInfo() {
        doFetch(`/decks/${deck_id}/review`,{})
        .then(response=>response.json())
        .then(result=>{
            setSelectedCard(result["card"]);
            let nNew = result["num_new"];
            let nDue = result["num_due"];
            let nEarly = result["num_early"];
            setNumDue(nDue);
            setNumNew(nNew);
            setNumEarly(nEarly);
        })
        .catch(e=>{
            setSelectedCard(undefined);
        });
    }

    function handleEditDeck(info) {
        if(info.action === 'delete') {
            setIsDeleted(true);
        } else {
            getDeckData();
            getDeckCards();
            getDeckReviewInfo();
        }
    }

    useEffect(function() {
        getDeckData();
        getDeckCards();
        getDeckReviewInfo();
    },[]);

    function handleFlashcardSaved(card) {
        getDeckCards();
    }

    if(isDeleted) {
        return (
            <Redirect to="/decks" />
        );
    }

    return (
        <div className="deck-container">
            <Row>
                <Col> <h1>{deckObj.name}</h1></Col>
            </Row>
            <Row>
                <Col md={0} lg={4}></Col>
                <Col>
                    <Stack gap={4} direction="horizontal" className="my-3 justify-content-center">
                        <ReviewModal onGetDeckReview={getDeckReviewInfo} deck_id={deck_id}  selectedCard={selectedCard} numNew={numNew} numDue={numDue} numEarly={numEarly} />
                        {userOwnsDeck() ?  <DeckFormModal deckObj={deckObj} title="Edit Deck" onSaveDeck={handleEditDeck}/> : <></>}
                        {userOwnsDeck() ? <FlashcardFormModal title="Add a new Card" buttonText="Add Card" onSaveFlashcard={handleFlashcardSaved}/> : <></>}
                    </Stack>
                </Col>
                <Col md={0} lg={4}></Col>
            </Row>
            <div className="deck-cards-preview">
                <FlashcardTable cards={deckCards} userOwnsDeck={userOwnsDeck()} onSaveFlashcard={handleFlashcardSaved} />
            </div>
        </div>
    );
}



export default Deck;
