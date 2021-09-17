from rest_framework.viewsets import ModelViewSet

from dictgame.models import Player, Event, Question
from dictgame.serializers import (
    PlayerSerializer, EventSerializer, QuestionSerializer
)

# Create your views here.


class PlayerViewSet(ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()


class QuestionViewSet(ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
