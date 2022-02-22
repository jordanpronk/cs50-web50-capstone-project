import React from 'react'
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { doFetch, doFetchPost, doFetchDelete } from '../FetchHelper';
import DeckFormModal from './DeckFormModal';
import Paginator from './Paginator';
import { Row, Col, Card, Button } from 'react-bootstrap';

function DeckList({subscribedOnly}) {

    const [decks,setDecks]=useState([]);
    const [pageInfo,setPageInfo]=useState();
    const [subscribedDecks,setSubscribedDecks]=useState([]);
    
    function fetchData(pageNum) {
        if(!pageNum) {
            if(pageInfo) {
                pageNum = pageInfo.current_page_num;
            } else {
                pageNum = 1;
            }
        }

        let deckUrl = `/decks?p=${pageNum}`;
        if(subscribedOnly) {
            deckUrl = `/user/subscriptions?p=${pageNum}`;
        }
        doFetch(deckUrl,{})
        .then(response=>response.json())
        .then(result=>{
            setDecks(result.decks);
            setPageInfo(result.page_info);
        })
        .catch(console.error);

        doFetch("/user/subscriptions",{})
        .then(response=>response.json())
        .then(result=>{
            setSubscribedDecks(result.decks);
        })
        .catch(console.error);
    }

    useEffect( function() {
        fetchData();
    },[]);

    function handleCreateDeck() {
        fetchData();
    }

    function handlePageSelected(pageNum) {
        fetchData(pageNum);
    }

    function handleDeckSubscribe(id, subscribe) {
        if(subscribe) {
            doFetchPost(`/user/subscriptions/deck/${id}`,{})
            .then(response=>response.json())
            .then(result=>{
                fetchData();
            })
            .catch(console.error);
        } else {
            doFetchDelete(`/user/subscriptions/deck/${id}`,{})
            .then(response=>response.json())
            .then(result=>{
                fetchData();
            })
            .catch(console.error);
        }
    }

    return (
        <>
        <Row>
            <Col md={0} lg={4}></Col>
            <Col>
            {decks.map(deck => (
                <div key={deck.id}>
                <Card className="text-center mb-3" >
                <Card.Body>
                    <Card.Title>{deck.name}</Card.Title>
                    <Card.Subtitle className="p-3 text-muted">
                        {deck.num_cards} Card{deck.num_cards > 1 || deck.num_cards === 0 ? "s" : ""}
                        <hr />
                        {deck.subscribers} Subscriber{deck.subscribers > 1 || deck.subscribers === 0 ? "s" : ""}
                    </Card.Subtitle>
                    <Card.Text>{deck.description}</Card.Text>
                    <Row >
                        <Col>
                            <Button as={Link} to={`/decks/${deck.id}`} variant="primary">View</Button>
                        </Col>
                        <Col>
                        {subscribedDecks.find(sub => sub.id === deck.id) ? 
                                <Button onClick={()=>handleDeckSubscribe(deck.id, false)} variant="secondary">Unsubscribe</Button>
                            :
                                <Button onClick={()=>handleDeckSubscribe(deck.id, true)} variant="secondary">Subscribe</Button>
                        }
                        </Col>
                    </Row>
                </Card.Body>
                </Card>
                </div>
            ))
            }
            <div className="text-center mb-3">
                <DeckFormModal title="Create Deck" onSaveDeck={handleCreateDeck}/>
            </div>

            <div>
                <hr />
                <Paginator page_info={pageInfo} onPageSelected={handlePageSelected}/>
            </div>

            </Col>
            <Col md={0} lg={4}>
            </Col>
        </Row>
        </>
      
    )
}

export default DeckList;