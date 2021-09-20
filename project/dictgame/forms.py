from django import forms

from dictgame.models import Player, Event, Question


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('key', )
