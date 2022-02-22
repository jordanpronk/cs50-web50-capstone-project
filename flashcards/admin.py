from django.contrib import admin

from flashcards.models import Card, Deck, CardReview, Rating, User

# Register your models here.
admin.site.register(Card)
admin.site.register(Deck)
admin.site.register(CardReview)
admin.site.register(Rating)
admin.site.register(User)