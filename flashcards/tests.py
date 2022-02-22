from datetime import timedelta
from django.utils import timezone
import json
from django.test import TestCase, Client
from flashcards.models import Deck, User, Card, CardReview
from flashcards.views import _get_prev_reviewed_cards


# Create your tests here.
class DeckTestCase(TestCase):
    def setUp(self) -> None:
        user_1 = User.objects.get_or_create(username="user1")[0]
        user_2 = User.objects.get_or_create(username="user2")[0]
        user_3 = User.objects.get_or_create(username="user3")[0]
        deck_1 = Deck.objects.create(name="Deck 1", description="description 1", creator=user_1)
        deck_2 = Deck.objects.create(name="Deck 2", description="description 2", creator=user_2)
        Card.objects.create(front_content="Foo1", back_content="bar1", deck=deck_1)
        Card.objects.create(front_content="Foo2", back_content="bar2", back_image_url="example.com/backimage", deck=deck_1)
        Card.objects.create(front_content="Foo3", front_image_url="example.com/frontimage", back_content="bar3", deck=deck_1)
        Card.objects.create(front_content="Foo", front_image_url="example.com/frontimage", back_content="bar", back_image_url="example.com/backimage", deck=deck_2)

    def test_list_decks(self):
        c = Client()
        c.force_login(User.objects.get_or_create(username="test_one")[0])
        response = c.get("/decks", content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["decks"][0]['name'], 'Deck 1')
        self.assertEqual(response.json()["decks"][1]['name'], 'Deck 2')

        deck_1 = response.json()["decks"][0]
        deck_2 = response.json()["decks"][1]

        response = c.get(f"/decks/{deck_1['id']}", content_type="json")
        self.assertEqual(response.status_code, 200)

        self.assertTrue("error" not in response.json())
        self.assertEqual(response.json()["id"], deck_1["id"])
        self.assertEqual(response.json()["name"], deck_1['name'])
        self.assertEqual(response.json()["subscribers"], 0)


        response = c.get(f"/decks/{deck_2['id']}", content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], deck_2['id'])
        self.assertEqual(response.json()["name"], deck_2['name'])

    def test_get_cards_for_a_deck(self):
        c = Client()
        c.force_login(User.objects.get_or_create(username="user1")[0])
        response = c.get("/decks/1/cards", content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()), 3)
        self.assertEqual(response.json()[0]["front_content"], "Foo1")
        self.assertEqual(response.json()[1]["front_content"], "Foo2")
        self.assertEqual(response.json()[1]["back_image_url"], "example.com/backimage")

        response = c.post("/decks/1/cards", data=json.dumps({"front_content":"front", "back_content":"back"}), content_type="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue("id" in response.json())
        self.assertEqual(response.json()["front_content"], "front")
        self.assertEqual(response.json()["back_content"], "back")
        card = Card.objects.get(id=response.json()["id"])
        self.assertEqual(card.front_content, "front")

    def test_deck_card_get_put_delete(self):
        c = Client()
        c.force_login(User.objects.get_or_create(username="user1")[0])
        response = c.get("/decks/1/cards/1", content_type="json")
        self.assertEqual(response.json()["front_content"], "Foo1")

        response = c.put("/decks/1/cards/1", data=json.dumps({"front_content":"front", "back_content":"back"}), content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["front_content"], "front")
        self.assertEqual(response.json()["back_content"], "back")
        self.assertEqual(response.json()["id"], 1)

        response = c.delete("/decks/1/cards/1", content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["front_content"], "front")
        self.assertEqual(response.json()["back_content"], "back")
        self.assertEqual(response.json()["id"], 1)


    def test_get_prev_reviewed_cards(self):
        # Not an endpoint - just a helper function test
        self.assertTrue(CardReview.objects.all().count() == 0)
        user = User.objects.get(id=1)
        alt_user = User.objects.get(id=2)
        deck = Deck.objects.get(name="Deck 1")
        alt_deck = Deck.objects.get(name="Deck 2")
        due_cards, early_cards = _get_prev_reviewed_cards(user, deck)

        deck_card_1 = deck.cards.get(id=1)
        deck_card_2 = deck.cards.get(id=2)
        alt_deck_card_1 = alt_deck.cards.get(id=4)

        # should be no reviewed cards, empty arrays
        self.assertEqual(len(due_cards), 0)
        self.assertEqual(len(early_cards), 0)

        review_date = timezone.now() - timedelta(minutes=5)
        due_date =  timezone.now() - timedelta(minutes=1)
        not_due_date =  timezone.now() + timedelta(minutes=1)
        
        # create some reviews manually

        rev_1 = CardReview.objects.create(user=user, review_date=review_date, due_date=due_date, card=deck_card_1)
        alt_rev = CardReview.objects.create(user=user, review_date=review_date, due_date=due_date, card=alt_deck_card_1)

        rev_alt_user_1 = CardReview.objects.create(user=alt_user, review_date=review_date, due_date=due_date, card=deck_card_1)
        rev_alt_user_2 = CardReview.objects.create(user=alt_user, review_date=review_date, due_date=due_date, card=deck_card_2)
        alt_rev_alt_user_1 = CardReview.objects.create(user=alt_user, review_date=review_date, due_date=due_date, card=alt_deck_card_1)
        
        # user has deck: due [deck_card_1] early []  alt_deck: due [alt_deck_card_1]  early []
        # alt user has deck: due [deck_card_1, deck_card_2] early []   alt_deck: due [alt_deck_card_1] early []

        # Test that the reviews are created, due and early are correct

        due_cards, early_cards = _get_prev_reviewed_cards(user, deck)
        self.assertEqual(len(due_cards), 1)
        self.assertEqual(len(early_cards), 0)

        rev_1.due_date = not_due_date # user, deck_card_1
        rev_1.save()

        # user has deck: due [] early [deck_card_1]  alt_deck: due [alt_deck_card_1]  early []
        # alt user has deck: due [deck_card_1, deck_card_2] early []   alt_deck: due [alt_deck_card_1] early []

        due_cards, early_cards = _get_prev_reviewed_cards(user, deck)

        self.assertEqual(len(due_cards), 0)
        self.assertEqual(len(early_cards), 1)
        self.assertTrue(deck_card_1.id in early_cards)

        due_cards, early_cards = _get_prev_reviewed_cards(user, alt_deck)

        self.assertEqual(len(due_cards), 1)
        self.assertEqual(len(early_cards), 0)
        self.assertTrue(alt_deck_card_1.id in due_cards)

        # Switch the user, test that there are no reviews with the other user

        # user has deck: due [] early [deck_card_1]  alt_deck: due [alt_deck_card_1]  early []
        # alt user has deck: due [deck_card_1, deck_card_2] early []   alt_deck: due [alt_deck_card_1] early []

        due_cards, early_cards = _get_prev_reviewed_cards(alt_user, deck)

        self.assertEqual(len(due_cards), 2)
        self.assertEqual(len(early_cards), 0)
        self.assertTrue(deck_card_1.id in due_cards)
        self.assertTrue(deck_card_2.id in due_cards)

        due_cards, early_cards = _get_prev_reviewed_cards(alt_user, alt_deck)

        self.assertEqual(len(due_cards), 1)
        self.assertEqual(len(early_cards), 0)
        self.assertTrue(alt_deck_card_1.id in due_cards)


    def test_card_review(self):
        self.assertTrue(CardReview.objects.all().count() == 0)

        c = Client()
        response = c.get("/decks/1/review", content_type="json")
        self.assertEqual(response.status_code, 401)

        c.force_login(User.objects.get_or_create(username="test_one")[0])

        # Get a random card to review
        response = c.get("/decks/1/review", content_type="json")
        self.assertEqual(response.status_code, 200) # gives a card in the deck
        self.assertEqual(response.json()["review_type"], "new")
        self.assertTrue(response.json()["card"] is not None)
        self.assertTrue(response.json()["card"]["front_content"] is not None)

        response = c.post("/decks/1/review", data=json.dumps({"card_id": 1, "difficulty": 3}), content_type="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["difficulty"], 3)
        self.assertTrue("id" in response.json())

        response = c.get("/decks/1/review", content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["review_type"] == "new") 
        self.assertEqual(response.json()["num_due"], 0)
        self.assertTrue(response.json()["card"] is not None)
        self.assertTrue(response.json()["card"]["front_content"] is not None)

        #set one due date back in the past
        card = CardReview.objects.get(id=1)
        card.due_date = due_date=timezone.now() - timedelta(minutes=5)
        card.save()

        response = c.get("/decks/1/review", content_type="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["review_type"],"due")
        self.assertEqual(response.json()["num_due"], 1)
        self.assertTrue(response.json()["card"] is not None)
        self.assertTrue(response.json()["card"]["front_content"] is not None)

        response = c.post("/decks/1/review", data=json.dumps({"card_id": 2, "difficulty": 3}), content_type="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["difficulty"], 3)
        self.assertTrue("id" in response.json())

        response = c.get("/decks/1/review", content_type="json")
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json()["review_type"], "due") # due is first priority
        self.assertEqual(response.json()["num_due"], 1) # still 1 item due
        self.assertTrue(response.json()["card"] is not None)
        self.assertTrue(response.json()["card"]["front_content"] is not None)

        card = CardReview.objects.get(id=2)
        card.due_date = due_date=timezone.now() - timedelta(minutes=1)
        card.save()

        response = c.get("/decks/1/review", content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["review_type"] == "due") # due is first priority
        self.assertEqual(response.json()["num_due"], 2) # now 2 items are due
        self.assertTrue(response.json()["card"] is not None)
        self.assertTrue(response.json()["card"]["front_content"] is not None)

        response = c.post("/decks/1/review", data=json.dumps({"card_id": 1, "difficulty": 1}), content_type="json")
        self.assertEqual(response.status_code, 201)
        response = c.post("/decks/1/review", data=json.dumps({"card_id": 2, "difficulty": 4}), content_type="json")
        self.assertEqual(response.status_code, 201)

        response = c.get("/decks/1/review", content_type="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["review_type"], "new") # due is first priority, new is second
        self.assertEqual(response.json()["num_due"], 0) 
        self.assertTrue(response.json()["card"] is not None)
        self.assertTrue(response.json()["card"]["front_content"] is not None)

        response = c.post("/decks/1/review", data=json.dumps({"card_id": 1, "difficulty": 1}), content_type="json")
        self.assertEqual(response.status_code, 201)
        response = c.post("/decks/1/review", data=json.dumps({"card_id": 2, "difficulty": 4}), content_type="json")
        self.assertEqual(response.status_code, 201)
        response = c.post("/decks/1/review", data=json.dumps({"card_id": 3, "difficulty": 5}), content_type="json")
        self.assertEqual(response.status_code, 201)

        response = c.get("/decks/1/review", content_type="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["review_type"], "early") # due is first priority, new is second
        self.assertEqual(response.json()["num_due"], 0) 
        self.assertEqual(response.json()["num_new"], 0) 
        self.assertEqual(response.json()["num_early"], 3) 
        self.assertTrue(response.json()["card"] is not None)
        self.assertTrue(response.json()["card"]["front_content"] is not None)

    def test_card_subscribe(self):
        c = Client()
        response = c.get("/user/subscriptions", content_type="json")
        self.assertEqual(response.status_code, 401)

        c.force_login(User.objects.get_or_create(username="test_one")[0])

        response = c.get("/user/subscriptions",  content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["decks"], [])

        response = c.get("/user/subscriptions/deck/1",  content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["subscribed"], False)
        response = c.get("/decks/1",  content_type="json")
        self.assertEqual(response.json()["subscribers"], 0) # check that subscribe count is zero

        response = c.post("/user/subscriptions/deck/1",  content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["subscribed"], True)
        response = c.get("/decks/1",  content_type="json") # check that subscribe count increased
        self.assertEqual(response.json()["subscribers"], 1)

        response = c.get("/user/subscriptions",  content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["decks"]), 1)

        response = c.delete("/user/subscriptions/deck/1", content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["subscribed"], False)
        response = c.get("/decks/1",  content_type="json") # check that subscribe count decreased
        self.assertEqual(response.json()["subscribers"], 0)

    def test_deck_rating(self):
        c = Client()
        response = c.get("/decks/1/rating", content_type="json")
        self.assertEqual(response.status_code, 401)

        c.force_login(User.objects.get_or_create(username="test_one")[0])
        response = c.get("/decks/1/rating", content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["deck_id"], 1)
        self.assertEqual(response.json()["average_ratings"], 0)
        self.assertEqual(response.json()["user_rating"], {})

        response = c.post("/decks/1/rating", data=json.dumps({'rating': 5}), content_type="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["deck_id"], 1)
        self.assertEqual(response.json()["rating"], 5)
        response = c.get("/decks/1/rating", content_type="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["deck_id"], 1)
        self.assertEqual(response.json()["average_ratings"], 5)
        self.assertEqual(response.json()["user_rating"]["rating"], 5)
