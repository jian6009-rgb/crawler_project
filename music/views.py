from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Song

def song_list(request):
    songs = Song.objects.all().order_by("id")
    paginator = Paginator(songs, 20)
    page_number = request.GET.get("pageNo")
    songs = paginator.get_page(page_number)

    return render(request, "music/song_list.html", {"songs": songs})

def song_detail(request, song_id):
    song = get_object_or_404(Song , id=song_id)

    return render(request, "music/song_detail.html", {"song": song})
