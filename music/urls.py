from django.urls import path
from . import views

urlpatterns = [
    path("", views.song_list, name="song_list"),
    path("song/<int:song_id>/", views.song_detail, name="song_detail"),
    path("artist/", views.artist_list, name="artist_list")
]