# Generated by Django 3.2.6 on 2021-10-19 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('flashcards', '0006_alter_deck_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='creator',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_decks', to=settings.AUTH_USER_MODEL),
        ),
    ]
