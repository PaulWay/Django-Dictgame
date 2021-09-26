from django.db.models import Count, F
from django.test import TestCase
from django.urls import reverse

# Create your tests here.

from dictgame.models import Player, Question


class constants():
    html_content_type = 'text/html; charset=utf-8'

    invalid_event_key = 'Nostalgic Burblings'
    event_key = 'examplicon'


class EntryViewTestCase(TestCase):
    fixtures = ['basic_test_data',]

    def test_basic_entry_page(self):
        response = self.client.get(reverse('entry'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], constants.html_content_type)
        self.assertIn('<html>', response.content.decode())

    def test_entry_form(self):
        # Slug too long, not a slug
        response = self.client.post(
            reverse('entry'),
            data={'key': constants.invalid_event_key},
        )
        self.assertEqual(response.status_code, 200)  # Not a 400
        self.assertEqual(response.headers['Content-Type'], constants.html_content_type)
        content = response.content.decode()
        self.assertIn('<html>', content)  # And it starts the usual way,
        self.assertIn('<ul class="errorlist">', content)  # but it has an error message

        # Valid slug gets redirected to a new page
        response = self.client.post(
            reverse('entry'),
            data={'key': constants.event_key},
        )
        # And we get redirected to the new page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('event', kwargs={'key': constants.event_key}))


class EventViewTestCase(TestCase):
    fixtures = ['basic_test_data', ]

    def test_no_list(self):
        response = self.client.get('/event/')
        self.assertEqual(response.status_code, 404)

    def test_basic_entry(self):
        response = self.client.get(
            reverse('event', kwargs={'key': constants.event_key})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], constants.html_content_type)
        content = response.content.decode()
        self.assertIn('<html>', content)
        self.assertIn("You're playing the 'Paul&#x27;s example dictionary game' Dictionary Game!", content)


class QuestionModelTestCase(TestCase):
    fixtures = ['basic_test_data',]

    def test_questions_have_definitions(self):
        # All questions must have at least one definition
        questions_with_no_definitions = Question.objects.filter(
            definitions__isnull=True
        )
        self.assertEqual(
            questions_with_no_definitions.count(), 0,
            "Questions with no definition: " +
            f"{questions_with_no_definitions}"
        )
        # Questions in state 1 - ready for definitions - should only have one
        # definition - the one that was set by their own dasher.
        ready_questions_with_many_definitions = Question.objects.annotate(
            def_count=Count('definitions')
        ).filter(state=1, def_count__gt=1)
        self.assertEqual(
            ready_questions_with_many_definitions.count(), 0,
            "Questions in state 1 with more than one definition: " +
            f"{ready_questions_with_many_definitions}"
        )
        questions_with_definition_from_other_dasher = Question.objects.filter(
            state=1
        ).exclude(
            definitions__player=F('dasher')
        )
        self.assertEqual(
            questions_with_definition_from_other_dasher.count(), 0,
            "Questions in state 1 whose dasher is not the definer: " +
            f"{questions_with_definition_from_other_dasher}"
        )

    def test_questions_appropriate_guesses(self):
        # Questions can't have guesses if they're in states 1 or 2 (ready to
        # show or being supplied with definitions).
        early_questions_with_guesses = Question.objects.filter(
            state__in=(1, 2, ), definitions__guesses__isnull=False
        )
        self.assertEqual(
            early_questions_with_guesses.count(), 0,
            "Questions that aren't ready to be voted on but have votes: " +
            f"{early_questions_with_guesses}"
        )

    def test_questions_one_guess_per_player(self):
        # We test this two ways - just in case there's a weird test case
        # I haven't though of in one of them.

        # 1: Each question can have at most one guess from each player
        guesses_per_question = Question.objects.values(
            'id', 'definitions__guesses__player_id'
        ).annotate(
            guess_count=Count('definitions__guesses')
        ).filter(guess_count__gt=1)
        self.assertEqual(
            guesses_per_question.count(), 0,
            "Questions that a player guessed more than once: " +
            f"{guesses_per_question}"
        )

        # 2: Players should have at most one guess per question
        guesses_per_player = Player.objects.values(
            'alias', 'guess__chose__question'
        ).annotate(
            guess_count=Count('guess__chose', distinct=True)
        ).filter(guess_count__gt=1)
        self.assertEqual(
            guesses_per_player.count(), 0,
            "Players with more than one guess on a question: " +
            f"{guesses_per_player}"
        )

        # We could also do:
        # Guess.objects.values('player', 'chose__question').annotate(guess_count=Count('id'))
        # But it tells us the same information as the above
