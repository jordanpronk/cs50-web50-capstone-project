
from django.db.models.aggregates import Avg
from django.db.models import Q
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.core.paginator import EmptyPage, Paginator

from django.db import transaction, IntegrityError

from .models import Deck, Rating, User, Card, CardReview
from django.urls import reverse
import json
import random

# Create your views here.

def _invalid_http_method_json():
    return JsonResponse({'error':'invalid request method'}, status=405)

def _get_not_found_json(id=""):
    return JsonResponse({'error':f'resource not found {id}'}, status=404)

def _not_authenticated_json():
    return JsonResponse({'error':'authentication required'}, status=401)

def _not_authorized_json():
    return JsonResponse({'error':'Unauthorized'}, status=403)

def _paginate_dict(queryset, queryset_key_str, serialize_func, selected_page_num, num_per_page=3):
    """
        serialize_func is a method that is mapped across all objects in page.object_list
    """
    p = Paginator(queryset.order_by("id"), num_per_page)
    page_obj = p.get_page(selected_page_num)
    return { queryset_key_str: [serialize_func(data_obj) for data_obj in page_obj.object_list], 
        "page_info":{
            "current_page_num": page_obj.number,
             "pages": p.num_pages
        }
    }

def user_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if "username" in data:
            username = data["username"]
        if "password" in data:
            password = data["password"]
            
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_authenticated:
            login(request, user)
            return JsonResponse({"user_id": user.id, "logged_in": True}, status=200)
        else:
            return JsonResponse({"logged_in": False, "error": "Invalid Credentials"}, status=401)

def user_logout(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"logged_in": False}, status=200)
    return _invalid_http_method_json()
    

def user_register(request):
    if request.method == "POST":

        if request.user.is_authenticated:
            return JsonResponse({"error": "Already logged in."}, status=400)

        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]
        confirmation = data["confirmation"]
        email = data["email"]

        # Ensure password matches confirmation
        if password != confirmation:
            return JsonResponse({"error": "Passwords must match."}, status=400)

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
        except IntegrityError:
            return JsonResponse({"error": "Username already taken."}, status=400)
        login(request=request, user=user)
        return JsonResponse({"user_id": user.id, "logged_in": user.is_authenticated}, status=200)
    else:
        return _invalid_http_method_json()

@ensure_csrf_cookie
def user(request):
    if request.method == "GET":
        if(request.user.is_authenticated):
            return JsonResponse({"user": request.user.serialize(), "logged_in": True}, status=200)
        else:
            return JsonResponse({"logged_in": False}, status=200)
    else:
        return _invalid_http_method_json()

def user_deck_subscriptions(request):
    """
    Get all the subscribed decks
        {subscribed_decks: [{deck_id: <int>, name: <str>}, ...] }
    """
    if not request.user.is_authenticated:
        return _not_authenticated_json()

    if request.method == "GET":
        decks = request.user.subscribed_decks.all()
        selected_page = request.GET.get('p', 1)
        data_dict = _paginate_dict(decks, "decks", lambda o: o.serialize(), selected_page_num=selected_page)
        return JsonResponse(data_dict, status=200)
    else:
        return _invalid_http_method_json()


def user_deck_subscription(request, deck_id):
    """
        Get shows if the user is subscribed to the deck
        Post to subscribe
        Delete to unsubscribe
    """
    if not request.user.is_authenticated:
        return _not_authenticated_json()

    try:
        deck = Deck.objects.get(pk=deck_id)
    except:
        return _get_not_found_json(deck_id)
    user = request.user
    is_subscribed = deck in user.subscribed_decks.all()
    if request.method == "GET":
        return JsonResponse({"deck_id":deck_id, "subscribed": is_subscribed}, status=200)
    elif request.method == "POST" or request.method == "PUT":
        if not is_subscribed:
            user.subscribed_decks.add(deck)
        return JsonResponse({"deck_id":deck_id, "subscribed": True}, status=200)
    elif request.method == "DELETE":
        if is_subscribed:
            user.subscribed_decks.remove(deck)
        return JsonResponse({"deck_id":deck_id, "subscribed": False}, status=200)
    else:
        return JsonResponse({'error':'invalid request method'}, safe=False, status=400)

def decks(request):
    """
        Returns all decks (name, id), but not cards etc.
        Used by the client to get ids for other URLs.
        POST to create a deck
            {name:<str>, description:<str>}
    """
    if not request.user.is_authenticated:
        return _not_authenticated_json()

    if request.method == "GET":
        decks = Deck.objects.all()
        selected_page = request.GET.get('p', 1)
        data_dict = _paginate_dict(decks, "decks", lambda o: o.serialize(), selected_page_num=selected_page)
        return JsonResponse(data_dict, status=200)
    elif request.method == "POST":
        data = json.loads(request.body)
        deck = Deck.objects.create(name=data["name"], description=data["description"], creator=request.user)
        deck.save()
        return JsonResponse(deck.serialize(), status=201)
    else:
        return _invalid_http_method_json()

def deck(request, deck_id):
    """
        Information about a specific deck. No cards.
    """
    if not request.user.is_authenticated:
        return _not_authenticated_json()

    try:
        deck_obj = Deck.objects.get(pk=deck_id)
    except:
        return _get_not_found_json(deck_id)

    if request.method == "GET":
        return JsonResponse(deck_obj.serialize(), status=200)
    elif request.method == "PUT":
        if deck_obj.creator != request.user:
            return _not_authorized_json()
        data = json.loads(request.body)
        deck_obj.name=data["name"]
        deck_obj.description=data["description"]
        deck_obj.save()
        return JsonResponse(deck_obj.serialize(), status=200)
    elif request.method == "DELETE":
        if deck_obj.creator != request.user:
            return _not_authorized_json()
        deck_obj.delete()
        return JsonResponse({"deleted": True}, status=200)
    else:
        return JsonResponse({'error':'invalid request method'}, safe=False, status=400)

def deck_cards(request, deck_id):
    """
        Requires authentication.
        GET Gets the cards (ids only) that belong to a deck. (200 ok)
            [{ "id": self.id,
            "front_content": self.front_content,
            "front_image_url": self.front_image_url,
            "back_content": self.back_content,
            "back_image_url": self.back_image_url}
            ... ]
        POST adds new card to the deck (201 ok)
            {   front_content: "Front side of card",
                back_content: "Back side of card",
                front_image_url: "example.com", <optional>
                back_image_url: "example.com" <optional>
            }
    """
    if not request.user.is_authenticated:
        return _not_authenticated_json()

    try:
        deck = Deck.objects.get(pk=deck_id)
    except:
        return _get_not_found_json(deck_id)
   
    if request.method == "GET":
        cards = deck.cards.all()

        return JsonResponse([card.serialize() for card in cards], safe=False, status=200)
    elif request.method == "POST":
        try:
            #if user does not own the deck, don't allow adding cards
            if request.user != deck.creator:
                return _not_authorized_json()
            with transaction.atomic():
                # add a new card to the deck's card collection
                data = json.loads(request.body)
                card = Card.objects.create(deck=deck, front_content=data["front_content"], back_content=data["back_content"])
                card.deserialize(data)
                card.save()
                return JsonResponse(card.serialize(), status=201)
        except:
            return JsonResponse({'error':'post failed'}, safe=False, status=500)
    else:
        return JsonResponse({'error':'invalid request method'}, safe=False, status=400)

def deck_card(request, deck_id, card_id):
    """
        GET Gets the information about a card.
        PUT Put to edit the card
        Delete to remove the card (must own the deck/card)
    """
    if not request.user.is_authenticated:
        return _not_authenticated_json()

    try:
        deck = Deck.objects.get(pk=deck_id)
    except:
        return _get_not_found_json(deck_id)

    try:
        card = deck.cards.get(pk=card_id)
    except:
        return _get_not_found_json(card_id)

    if request.method == "GET":
        return JsonResponse(card.serialize(), status=200)
    elif request.method == "PUT":
        if request.user != deck.creator:
            return _not_authorized_json()
        try:
            # add a new card to the deck's card collection
            data = json.loads(request.body)
            card.deserialize(data)
            card.save()
            return JsonResponse(card.serialize(), status=200)
        except:
            return JsonResponse({'error':'put failed'}, safe=False, status=500)
    elif request.method == "DELETE":
        if request.user != deck.creator:
            return _not_authorized_json()
        try:
            serialized_data = card.serialize()
            card.delete()
            return JsonResponse(serialized_data, status=200)
        except:
            return JsonResponse({'error':'delete failed'}, safe=False, status=500)
    else:
        return JsonResponse({'error':'invalid request method'}, safe=False, status=400)


def _get_prev_reviewed_cards(user, deck):
    """
    Returns a tuple of (set[due cards],set[not due cards])
    where each card data the pk of the card
    """
    review_qs = CardReview.objects.filter(user=user, card__deck=deck).values_list("card__id", "due_date").order_by("card__id")

    due_cards = set()
    early_cards = set()

    current_time = timezone.now()

    for card_id, due_date in review_qs.all():
        if due_date > current_time:
            early_cards.add(card_id)
        elif due_date <= current_time:
            due_cards.add(card_id)

    return frozenset(due_cards), frozenset(early_cards)


def deck_review(request, deck_id):
    """
    GET Get the next card to review from the deck
        returns 
        {
            "type": < due | new | early | empty >
            "card": {
                "id": self.id,
                "front_content": self.front_content,
                "front_image_url": self.front_image_url,
                "back_content": self.back_content,
                "back_image_url": self.back_image_url
            }
        }
        Note: due means previously review and it is time to review again, 
            new means never seen the card before, 
            early means there are no due reviews and no new cards so review a card before it is due
            empty means there are no cards in the deck
        or returns the following when there are no cards
         "review_type": <due|new|early|empty>
            "card": null
    POST to create/update the last review
        {
            card_id: <int> id of the card reviewed
            difficulty: <1-5> difficulty to remember card
        }
    """
    if not request.user.is_authenticated:
        return _not_authenticated_json()
    try:
        deck = Deck.objects.get(pk=deck_id)
    except:
        return _get_not_found_json(deck_id)
   
    if request.method == "GET":
        try:
            # get frozenset of due cards, not yet due cards
            due_cards_set, early_cards_set = _get_prev_reviewed_cards(request.user, deck)

            new_cards_qs = deck.cards.values_list("id", flat=True).order_by("id").all()

            new_cards_set = { id for id in new_cards_qs }
            new_cards_set -= due_cards_set # set difference to remove reviewed cards, leaving only 'new' cards
            new_cards_set -= early_cards_set

            # ideally choose a due card, then second choice is a new card
            next_cards_set = due_cards_set if len(due_cards_set) > 0 else frozenset(new_cards_set)

            if len(next_cards_set) == 0:
                next_cards_set |= early_cards_set # if no due/new cards, show not due cards early reviews
          
            next_card = None
            card_type_str = "empty"

            if len(next_cards_set) > 0:
                next_card_id = random.choice(list(next_cards_set))
                next_card = Card.objects.get(id=next_card_id)
                if next_card_id in due_cards_set:
                    card_type_str = "due"
                elif next_card_id in new_cards_set:
                    card_type_str = "new"
                elif next_card_id in early_cards_set:
                    card_type_str = "early"

            return JsonResponse({
                "review_type": card_type_str,
                "card": next_card.serialize() if next_card is not None else None,
                "num_due": len(due_cards_set),
                "num_new": len(new_cards_set),
                "num_early": len(early_cards_set),
            }, status=200)
        except Exception as ex:
            return _get_not_found_json()
    elif request.method == "POST":
        data = json.loads(request.body)
        card_id = data["card_id"]
        try:
            card = deck.cards.get(pk=card_id)
        except:
            return _get_not_found_json(card_id)
        try:
            difficulty = data["difficulty"]
            with transaction.atomic():
                review, created = CardReview.objects.get_or_create(user=request.user, card=card,)
                review.set_due_date(difficulty)
                review.deserialize(data)
                review.save()
                return JsonResponse(review.serialize(), status=201)
        except Exception as ex:
            return JsonResponse({'error':'post failed'}, safe=False, status=500)
    else:
        return JsonResponse({'error':'invalid request method'}, status=400)

def deck_rate(request, deck_id):
    if not request.user.is_authenticated:
        return _not_authenticated_json()
    try:
        deck = Deck.objects.get(pk=deck_id)
        average_ratings = deck.ratings.aggregate(Avg('rating'))
        if average_ratings['rating__avg'] is not None:
            average_ratings = average_ratings['rating__avg']
        else:
            average_ratings = 0

        user_rating = deck.ratings.filter(user=request.user).first()

    except:
        return _get_not_found_json(deck_id)

    if request.method == "GET":
        return JsonResponse({"deck_id":deck_id, "average_ratings": average_ratings, "user_rating": user_rating.serialize() if user_rating is not None else {}}, status=200)
    elif request.method == "POST":
        try:
            with transaction.atomic():
                if deck.ratings.filter(user=request.user).count() > 0:
                    return JsonResponse({'error':'post failed, resource already exists'}, status=400)    
                # add a new review to the card
                data = json.loads(request.body)
                rating, created = Rating.objects.get_or_create(user=request.user, rating=data["rating"], deck=deck)
                if not created:
                    rating.delete()
                    return JsonResponse({'error':'post failed, resource already exists'}, status=400)    
                rating.deserialize(data)
                rating.save()
                return JsonResponse(rating.serialize(), status=201)
        except:
            return JsonResponse({'error':'post failed'}, status=500)
    elif request.method == "PUT":
        pass
    elif request.method == "DELETE":
        pass
    else:
        return JsonResponse({'error':'invalid request method'}, safe=False, status=400)
