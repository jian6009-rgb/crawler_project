import json
from django.conf import settings
from django.core.management.base import BaseCommand
from music.models import Artist, Song


class Command(BaseCommand):
    help = "将歌曲和歌手的数据导入py数据库"
    def handle(self, *args, **options):
        song_path = settings.BASE_DIR / "data" / "songs.json"
        artist_path = settings.BASE_DIR / "data" / "artists.json"
        with song_path.open("r", encoding="utf-8") as savefile:
            songs_data = json.load(savefile)
        with artist_path.open("r", encoding="utf-8") as savefile:
            artists_data = json.load(savefile)

        artist_objects = {}
        
        for artist_data in artists_data:
            artist_url = artist_data.get("artist_url")

            artist, state = Artist.objects.update_or_create(
                original_url=artist_url,
                defaults={
                    "name": artist_data.get("artist_name", ""),
                    "image_url": artist_data.get("artist_image_url",""),
                    "intro": artist_data.get("artist_intro", "")
                }
            )

            artist_objects[artist_url] = artist

        song_objects = {}

        # 再把歌曲加入数据库
        for song_data in songs_data:
            song_url = song_data.get("song_url")

            song, _ = Song.objects.update_or_create(
                original_url=song_url,
                defaults={
                    "name": song_data.get("song_name", ""),
                    "lyrics": song_data.get("lyrics", ""),
                    "cover_url": song_data.get("cover_url") or ""
                }
            )

            song_objects[song_url] = song

        # 根据artists.json建立歌曲与歌手的关系
        for artist_data in artists_data:
            artist_url = artist_data.get("artist_url")
            artist = artist_objects.get(artist_url)
            artist_songs = artist_data.get("songs", [])

            for song_data in artist_songs:
                song_url = song_data.get("song_url")
                song = song_objects.get(song_url)

                if song is not None:
                    song.artists.add(artist)

        print("ok")