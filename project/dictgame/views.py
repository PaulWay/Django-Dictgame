from django.shortcuts import render
from django.views import View

from rest_framework.viewsets import ModelViewSet

from dictgame.forms import EventForm
from dictgame.models import Player, Event, Question
from dictgame.serializers import (
    PlayerSerializer, EventSerializer, QuestionSerializer
)

# Create your views here.


#############################################################################
# API views


class PlayerViewSet(ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()


class QuestionViewSet(ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


#############################################################################
# Regular views?


class EntryView(View):
    form_class = EventForm
    template_name = 'index.html'

    def get(self, request):
        form = self.form_class()
        return render(self.template_name, {
            'entry_form': form,
        })

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse(
                'event', kwargs={'key': form.validated_data['key']}
            ))
        return render(self.template_name, {
            'entry_form': form,
        })


class EventView(View):
    template_name = 'event.html'
    def get(self, request, key):
        event = get_object_or_404(Event, key=key)
        return render(self.template_name, {
            'event': event,
        })

