from django.contrib.auth.models import User
from django.db import models


class Player(models.Model):
    # Some users can log in, but most players are just created on spec
    user = models.ForeignKey(User, default=None, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=64)
    alias = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.alias} ({self.name})"


class Event(models.Model):
    key = models.SlugField(max_length=16)
    name = models.CharField(max_length=250)
    host = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} hosted by {self.host.alias}"


class Question(models.Model):
    THEME_CHOICES = [
        ('W', 'Word'),
        ('O', 'Organisation'),
        ('M', 'Movie plot'),
        ('P', 'Person'),
        ('D', 'Date')
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='questions')
    dasher = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='proposed_questions')  # the person who proposed the question
    word = models.CharField(max_length=64)
    theme = models.CharField(max_length=1, choices=THEME_CHOICES)
    state = models.CharField(max_length=1, choices=[
        ('1', 'Ready to be shown'),
        ('2', 'Word being shown, ready for definitions'),
        ('3', 'Definitions being voted on, ready for scoring'),
        ('4', 'Scoring done'),
    ])

    def __str__(self):
        return f"{self.id}: question in {self.event.name} (theme {self.theme}, state {self.state})"


class Definition(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='proposed_definitions')
    question = models.ForeignKey(Question, related_name='definitions', on_delete=models.CASCADE)
    definition = models.TextField()

    def votes_for(self):
        """
        How many votes does this definition have?  This indicates the score
        for the person who proposed this definition.
        """
        count = self.guesses.filter(guess__player=self.player).count()
        # If this is the 'correct' definition, is there a multiplier?
        return count

    def __str__(self):
        return f"{self.id}: definition for question {self.question_id} by {self.player.alias}"


class Guess(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    chose = models.ForeignKey(Definition, related_name='guesses', on_delete=models.CASCADE)
    score = models.SmallIntegerField(default=0, null=True)

    def calc_score(self):
        """
        Calculate the score for this guess.  Should only be called when the
        question is ready for scoring.  Does not calculate the player's score
        for other people guessing their definition.
        """
        # If the question isn't ready to be scored, return None
        if self.chosen.question.state < 3:
            return None
        # If this player guessed their own definition, then they get -1
        if self.player == self.chosen.player:
            return -1
        # If this player guessed the correct definition, they get 3
        # The correct definition is the one submitted by the question's dasher
        if self.chosen.question.dasher == self.chosen.player:
            return 3
        # The question of whether anyone else voted for this player's
        # definition is handled in the definition
        # Otherwise they get nothing
        return 0

    def __str__(self):
        return f"{self.id}: {self.player.alias} chose answer {self.chosen_id} in question {self.chosen.question_id}"
