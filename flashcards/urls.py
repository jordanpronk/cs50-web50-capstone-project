from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('user/login', views.user_login),
    path('user/logout', views.user_logout),
    path('user/register', views.user_register),
    path('user/subscriptions', views.user_deck_subscriptions),
    path('user/subscriptions/deck/<int:deck_id>', views.user_deck_subscription),
    path('user', views.user),
    path('decks', views.decks),
    path('decks/<int:deck_id>', views.deck),
    path('decks/<int:deck_id>/review', views.deck_review),
    path('decks/<int:deck_id>/cards', views.deck_cards),
    path('decks/<int:deck_id>/cards/<int:card_id>', views.deck_card),
    path('decks/<int:deck_id>/rating', views.deck_rate)
]
