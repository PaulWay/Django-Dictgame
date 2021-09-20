from django.contrib import admin

# Register your models here.

from dictgame.models import Event, Player, Question


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass
