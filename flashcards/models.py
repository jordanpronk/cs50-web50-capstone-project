from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Deck(models.Model):
    name = models.TextField(max_length=64, blank=False)
    description = models.TextField(max_length=256, blank=False, default="")
    creator = models.ForeignKey(to="User", null=True, blank=False, default=None, on_delete=models.CASCADE, related_name="owned_decks")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "subscribers": self.subscribers.count(),
            "num_cards": self.cards.count(),
            "creator_id": self.creator.id if self.creator is not None else None
        }

class User(AbstractUser):
    created = models.DateTimeField(blank=False, auto_now_add=True)
    modified = models.DateTimeField(blank=False, auto_now=True)
    subscribed_decks = models.ManyToManyField(to=Deck, blank=True, symmetrical=False, related_name="subscribers")
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username
        }

class Rating(models.Model):
    user = models.ForeignKey(to=User, blank=False, null=False, on_delete=models.CASCADE, related_name="ratings")
    deck = models.ForeignKey(to=Deck, blank=False, null=False, on_delete=models.CASCADE, related_name="ratings")
    rating = models.SmallIntegerField(blank=False, null=False, validators=[MinValueValidator(1), MaxValueValidator(5)])
    def serialize(self):
        return {
            "user": self.user.id,
            "deck_id": self.deck.id,
            "rating": self.rating
        }

    def deserialize(self, data):
        if "rating" in data: self.rating = data["rating"]


class Card(models.Model):
    front_content = models.TextField(max_length=96, blank=True)
    front_image_url = models.URLField(blank=True)
    back_content = models.TextField(max_length=96, blank=True)
    back_image_url = models.URLField(blank=True)
    deck = models.ForeignKey(to=Deck, blank=False, null=False, on_delete=models.CASCADE, related_name="cards")

    def serialize(self):
        return {
            "id": self.id,
            "front_content": self.front_content,
            "front_image_url": self.front_image_url,
            "back_content": self.back_content,
            "back_image_url": self.back_image_url
        }
    def deserialize(self, data):
        if "front_content" in data: self.front_content = data["front_content"] 
        if "front_image_url" in data: self.front_image_url = data["front_image_url"] 
        if "back_content" in data: self.back_content = data["back_content"]
        if "back_image_url" in data: self.back_content = data["back_image_url"]

class CardReview(models.Model):
    user = models.ForeignKey(to=User, blank=False, null=False, on_delete=models.CASCADE, related_name="card_reviews")
    review_date = models.DateTimeField(blank=False, auto_now=True)
    due_date = models.DateTimeField(blank=False, default=timezone.now)
    difficulty = models.SmallIntegerField(blank=False, null=False, validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name="card_reviews")

    def set_due_date(self, difficulty):
        self.difficulty = difficulty
        now = timezone.now()
        if difficulty <= 1: # Easy
            self.due_date = now + timedelta(minutes=5)
        elif difficulty <= 3: #Normal
            self.due_date = now + timedelta(minutes=2)
        elif difficulty <= 5: #Hard
            self.due_date = now + timedelta(minutes=1)
        else:
            raise Exception(f"Invalid difficulty of {difficulty}")

    def serialize(self):
        return {
            "id": self.id,
            "card_id": self.card.id,
            "user": self.user.id,
            "difficulty": self.difficulty,
            "review_date": self.review_date,
            "due_date": self.due_date
        }
    def deserialize(self, data):
        if "difficulty" in data: self.difficulty = data["difficulty"]
        if "card_id" in data: self.card.id = data["card_id"]
