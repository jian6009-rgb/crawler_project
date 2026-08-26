from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Artist, Song
import time
from django.db.models import Case,Q,Value,When

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

def search_results(request):
    start_time = time.perf_counter()
    keyword = request.GET.get( "keyword","" ).strip()[:20]
    search_type = request.GET.get( "search_type", "song" )
    page_number = request.GET.get("pageNo")

    if not keyword:
        if search_type == "artist":
            results = Artist.objects.none()
        else:
            search_type = "song"
            results = Song.objects.none()
    else:
        if search_type == "song":
            results = Song.objects.filter(
                Q(name__icontains = keyword)
                |Q(singer_name__icontains = keyword)
                |Q(lyrics__icontains = keyword)).annotate(
                match_level = Case(
                    When(name__iexact=keyword,then=Value(4)),
                    When(name__icontains=keyword,then=Value(3)),
                    When(singer_name__icontains=keyword,then=Value(2)),
                    When(lyrics__icontains=keyword,then=Value(1)),
                    default=Value(0)
                )
                ).order_by("-match_level","name")
        else:
            search_type = "artist"
            results = Artist.objects.filter(
                Q(name__icontains = keyword)
                |Q(intro__icontains = keyword)).annotate(
                match_level = Case(
                    When(name__iexact=keyword,then=Value(4)),
                    When(name__icontains=keyword,then=Value(3)),
                    When(intro__icontains=keyword,then=Value(2)),
                    default=Value(0)
                )
                ).order_by("-match_level","name")

    paginator = Paginator(results, 10)
    results = paginator.get_page(page_number)
    list(results.object_list)
    result_num = paginator.count
    
    timing = time.perf_counter() - start_time

    start = max(1, results.number - 2)
    end = min(paginator.num_pages,results.number + 2)
    allpages = range(start,end+1)

    return render(
    request,
    "music/search_results.html",
    {
        "keyword": keyword,
        "search_type": search_type,
        "results": results,
        "result_num": result_num,
        "search_time": f"{timing:.4f}",
        "allpages": allpages
    }
    )
    
    

