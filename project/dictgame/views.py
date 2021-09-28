from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View

from rest_framework.viewsets import ModelViewSet

from dictgame.forms import EventForm, PlayerForm, WordAndDefinitionForm
from dictgame.models import Player, Event, Question, Definition
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
        return render(request, self.template_name, {
            'entry_form': form,
        })

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse(
                'event', kwargs={'key': form.cleaned_data['key']}
            ))
        return render(request, self.template_name, {
            'entry_form': form,
        })


def get_player(request, event, template):
    """
    Get the player object based on session variables.  If that fails, hand
    back a rendered template for the form.
    """
    # Find the player by their name and alias
    player_name = request.session.get('player_name', None)
    player_alias = request.session.get('player_alias', None)
    if not (player_name and player_alias):
        # Use standard page but try to be adaptive for HTMX integration?
        return render(request, template, {
            'event': event,
            'player_form': PlayerForm(),
        })
    # Don't return a 404 here, just show the form again
    try:
        player = Player.objects.get(name=player_name, alias=player_alias)
    except Player.DoesNotExist:
        # Use standard page but try to be adaptive for HTMX integration?
        player = None
    return player


def full_page_render(request, event, player, template):
    questions = event.questions.filter(
        state=2,
    ).prefetch_related(
        # A list of the definition submitted by the current player
        Prefetch(
            'definitions', Definition.objects.filter(player=player),
            to_attr='my_definition'
        ),
        # A list of the definition guessed by the current player
        Prefetch(
            'definitions', Definition.objects.filter(guesses__player=player),
            to_attr='my_guess'
        ),
    )
    print([
        f"q {q}: {q.my_definition=}"
        for q in questions
    ], [
        f"q {q}: {q.my_guess=}"
        for q in questions
    ])

    return render(request, template, {
        'event': event,
        'player': player,
        'questions': questions,
        'my_questions': event.questions.filter(dasher=player),
        'player_submit_question': not event.questions.filter(dasher=player).exists(),
        'word_and_definition_form': WordAndDefinitionForm(),
    })


class EventView(View):
    template_name = 'event.html'
    def get(self, request, key):
        event = get_object_or_404(Event, key=key)
        player = get_player(request, event, self.template_name)
        if not isinstance(player, Player):
            return player  # it's the render of the form
        return full_page_render(request, event, player, self.template_name)

    # Handles leaving and player naming only, all other actions handled via
    # HTMX forms
    def post(self, request, key):
        event = get_object_or_404(Event, key=key)
        if 'leave_game' in request.POST:
            if 'player_name' in request.session and 'player_alias' in request.session:
                del(request.session['player_name'])
                del(request.session['player_alias'])
            return HttpResponseRedirect(reverse('entry'))
        # Name form
        if 'name' in request.POST:
            player_form = PlayerForm(request.POST)
            if not player_form.is_valid():
                return render(request, self.template_name, {
                    'event': event,
                    'player_form': player_form,
                })
            # Save the player's info in their session
            request.session['player_name'] = player_form.cleaned_data['name']
            request.session['player_alias'] = player_form.cleaned_data['alias']
            # Find a record for them, or create it.
            player, created = Player.objects.update_or_create(
                name=player_form.cleaned_data['name'],
                alias=player_form.cleaned_data['alias'],
            )
        else:
            player = get_player(request, event, 'event_body.html')
            if not isinstance(player, Player):
                return player  # it's the render of the form

        # This doesn't use HTMX so it's the full page.
        return full_page_render(request, event, player, self.template_name)


class EventFormsView(View):
    """
    Handle HTMX event page form interactions
    """

    def get(self, request, key):
        """
        Used to get the initial form object for the template, based on the
        'form' parameter.  Any choice of what to get is supplied
        in the query parameters.
        """
        if 'form' not in request.GET:
            print("WARNING: EventForms get with no form parameter")
            return full_page_render(request, event, player, 'event_body.html')
        form_name = request.GET['form']


    def post(self, request, key):
        template_name = 'event_body.html'
        form = None
        event = get_object_or_404(Event, key=key)
        # New player and leaving should be handled by event view

        # Otherwise, we assume we have the player set in the session
        player = get_player(request, event, 'event.html')
        if not isinstance(player, Player):
            return player  # it's the render of the form

        if 'word_form' in request.POST:
            wnd_form = WordAndDefinitionForm(request.POST)
            if wnd_form.is_valid():
                # Create new question:
                q = Question(
                    event=event, dasher=player,
                    word=wnd_form.cleaned_data['word'],
                    theme=wnd_form.cleaned_data['theme'],
                    state=1
                )
                q.save()
                # Create the new definition:
                a = Definition(
                    player=player, question=q,
                    definition=wnd_form.cleaned_data['definition']
                )
            template = 'event_player_submit_word.html'

        else:
            print(f"{request.POST=}")

        return full_page_render(request, event, player, template_name)
