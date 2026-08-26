from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Artist, Song

def song_list(request):
    songs = Song.objects.all().order_by("id")
    paginator = Paginator(songs, 20)
    page_number = request.GET.get("pageNo")
    songs = paginator.get_page(page_number)

    start = max(1, songs.number - 2)
    end = min(paginator.num_pages,songs.number + 2)
    allpages = range(start,end+1)
    


    return render(request, "music/song_list.html", {"songs": songs,"allpages": allpages})

def song_detail(request, song_id):
    song = get_object_or_404(Song , id=song_id)

    return render(request, "music/song_detail.html", {"song": song})

def artist_list(request):
    artists = Artist.objects.all().order_by("id")
    paginator = Paginator(artists, 20)
    page_number = request.GET.get("pageNo")
    artists = paginator.get_page(page_number)
    start = max(1, artists.number - 2)
    end = min(paginator.num_pages,artists.number + 2)
    allpages = range(start,end+1)

    return render(request, "music/artist_list.html", {"artists": artists,"allpages": allpages})

def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist , id=artist_id)

    return render(request, "music/artist_detail.html", {"artist": artist})
