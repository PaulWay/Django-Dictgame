from rest_framework import serializers

from dictgame import models


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Player
        field = ('name', 'alias')


class EventSerializer(serializers.ModelSerializer):
    host = PlayerSerializer(many=False)

    class Meta:
        model = models.Event
        fields = ('name', 'host')


class DefinitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Definition
        fields = ('definition',)


class QuestionSerializer(serializers.ModelSerializer):
    definitions = DefinitionSerializer(many=True, source='definitions')

    class Meta:
        model = models.Question
        fields = ('word', 'type')

class GuessSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Guess
        fields = ('player', 'chosen_id', 'scored', 'score')
