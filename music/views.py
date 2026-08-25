from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Song

def song_list(request):
    songs = Song.objects.all().order_by("id")
    paginator = Paginator(songs, 20)
    page_number = request.GET.get("pageNo")
    songs = paginator.get_page(page_number)

    return render(request, "music/song_list.html", {"songs": songs})
