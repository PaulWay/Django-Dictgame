from django.urls import include, path

from dictgame import views

urlpatterns = [
    path(r'event/<str:key>', views.EventView.as_view(), name='event'),
    # The HTMX form handlers
    path(r'eventforms/<str:key>', views.EventFormsView.as_view(), name='eventforms'),
    # And last, the entry?
    path('', views.EntryView.as_view(), name='entry'),
]
