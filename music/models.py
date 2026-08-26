from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=200)
    image_url = models.URLField(blank=True,default="")
    intro = models.TextField(blank=True, default="")
    original_url = models.URLField(unique=True)
    wikipedia_url = models.URLField(blank=True, default="")
    def __str__(self):
        return self.name


class Song(models.Model):
    name = models.CharField(max_length=200)
    singer_name = models.CharField(max_length=200,blank=True,default="")
    lyrics = models.TextField()
    cover_url = models.URLField(blank=True)
    original_url = models.URLField(unique=True)
    artists = models.ManyToManyField(Artist,related_name="songs")
    def __str__(self):
        return self.name