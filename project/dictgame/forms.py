from django import forms
from django.core.exceptions import ValidationError

from dictgame.models import Player, Event, Question


def existing_event(key):
    return Event.objects.filter(key=key).exists()


class EventForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if not existing_event(cleaned_data.get('key', '')):
            raise ValidationError('Key not known')
        return cleaned_data

    class Meta:
        model = Event
        fields = ('key', )


class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        fields = ('name', 'alias')
