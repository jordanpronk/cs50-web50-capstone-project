import React from 'react'
import { Table, Fade } from 'react-bootstrap';
import FlashcardFormModal from './FlashcardFormModal';


export function FlashcardTable({cards, userOwnsDeck, onSaveFlashcard}) {

    return (
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Front</th>
            <th>Back</th>
          </tr>
        </thead>
        <tbody>
          { cards.map(card => 
            <tr key={card.id}>
              <td>{card.front_content}</td>
              <td>{card.back_content}</td>
              {userOwnsDeck ?  <td><FlashcardFormModal cardObj={card} title="Edit Card" buttonText="Edit" onSaveFlashcard={onSaveFlashcard} /></td> : <></>}
            </tr>
          )}
        </tbody>
      </Table>
    );
}

export default function Flashcard({front, back, showFront}) {
    if(showFront) {
      return (
        <div className="flashcard-review-container" style={{minHeight: '150px'}}>
          <div>
            {front}
            <hr />
          </div>
        </div>
      )
    } else {
      return (
        <div className="flashcard-review-container" style={{minHeight: '150px'}}>
          <div>
            {front}
            <hr />
          </div>
            <Fade in={true} appear={true} dimension="horizontal">
              <div>
                  {back}
              </div>
            </Fade>
        </div>
      )
    }
}

