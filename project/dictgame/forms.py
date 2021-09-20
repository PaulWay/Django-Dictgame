from django import forms

from dictgame.models import Player, Event, Question


def existing_event(key):
    return Event.objects.filter(key=key).exists()


class EventForm(forms.ModelForm):
    key = forms.SlugField(validators=[existing_event])

    class Meta:
        model = Event
        fields = ('key', )
