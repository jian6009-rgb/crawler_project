from urllib.parse import urljoin
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
import re
import random
import time

#新增一些注释：由于Kugou一直有一些防止爬虫的东西，因此改用qianqian音乐，这一个代码是几乎复制crawler_kugo.py，可在那里找到原代码
SONG_LIST_URL = "https://music.taihe.com/search?word=爱"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.8.7271 SLBChan/115 SLBVPV/64-bit"
HEADERS = {"User-Agent": USER_AGENT}
DATA_PATH = Path("data/qiansongs.json")

def create_urllist(head, tail):
    url_list = []
    for page_num in range(head, tail + 1):
        url = ("https://music.91q.com/artist/A10081787")
        url_list.append(url)
    return url_list
    
def getrank_songs(rank_url):
    response = requests.get(rank_url,headers=HEADERS,timeout=15)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    song_tags = soup.select('a[href*="/song/"]')
    
    songs = []
    for song_tag in song_tags:
        song_name = song_tag.get_text(strip=True)
        song_url = song_tag.get("href")
        song_url = urljoin(rank_url,song_url) 
        #千千很喜欢用相对链接，所以要用urljoin

        song = {"song_name": song_name,"song_url": song_url}
        songs.append(song)
    return songs


def getsong_detail(song):
    response = requests.get(song["song_url"],headers=HEADERS,timeout=15)
    response.raise_for_status()
    html = response.text
    lyric_match = re.search(r'lyric:"([^"]+)"',html) 
    #千千很喜欢用txt来表示歌词

    if lyric_match is None:
        raise ValueError("没有找到歌词URL")
    lyric_url = lyric_match.group(1).replace(r"\u002F","/")


    
    lyric_response = requests.get(lyric_url,headers=HEADERS,timeout=15)
    lyric_response.raise_for_status()
    lyric_response.encoding = "utf-8"
    rawlyrics = lyric_response.text.strip()
    lyrics = re.sub(r"\[\d{1,2}:\d{2}(?:\.\d+)?\]","",rawlyrics).strip()
    if len(lyrics)<20: 
        #千千有些歌词会写：暂无歌词，所以要判断歌词长度
        raise ValueError("没有找到歌词URL")

    cover_match = re.search(r'pageData:\{artist:\[.*?\],cpId:[^,]+,pic:"([^"]+)"',html,flags=re.DOTALL #去掉时间

    if cover_match is not None:
        cover_url = cover_match.group(1).replace(r"\u002F","/")
    else:
        cover_url = None


    soup = BeautifulSoup(html,"html.parser")
    singer_tags = soup.select('.info .artist a[href*="/artist/"]')

    singer_names = []
    singer_urls = []
    for singer_tag in singer_tags:
        singer_name = singer_tag.get_text(strip=True)
        singer_url = singer_tag.get("href")
        singer_url = urljoin(song["song_url"],singer_url)
        singer_names.append(singer_name)
        singer_urls.append(singer_url)

    singer_name = "/".join(singer_names)
    song["singer_name"] = singer_name
    song["singer_urls"] = singer_urls
    song["lyrics"] = lyrics
    song["cover_url"] = cover_url
    return song


def savesong(songs):
    with DATA_PATH.open("w",encoding="utf-8") as savefile:
        json.dump(songs,savefile,ensure_ascii=False,indent=2)


def playwrit():
    songs = []
    for url in create_urllist(1,1): #手动调整create_urllist(x,y)来决定爬哪几页，最主要怕一次性爬所有会崩溃（kugou带来的阴影）
        for attempt in range(1, 3): #有时候qianqian输入网站会有不知名错误，多试几遍就好了
            try:
                songs.extend(getrank_songs(url))
                break

            except Exception as error:
                print(attempt,":",error)
                time.sleep(5)

        delay = random.uniform(2, 3)
        time.sleep(delay)
        

    
    if DATA_PATH.exists():#断点续爬
        with DATA_PATH.open("r", encoding="utf-8") as savefile:
            detail_songs = json.load(savefile)
    else:
        detail_songs = []
        
    saved_urls = []
    for saved_song in detail_songs:
        saved_urls.append(saved_song["song_url"])
    new_songs = []
    for song in songs:
        if song["song_url"] not in saved_urls:
            new_songs.append(song)
    songs = new_songs
    consecutive_failures = 0

    
    for idx, song in enumerate(songs,start=1): #写consecutive_failures一开始是因为我不会怎么在代码出错时关terminal，不过现在会了但觉得这个功能有点用就没有删
        print(f"{idx}:{song['song_name']}")

        try:
            detail_song = getsong_detail(song)
            detail_songs.append(detail_song)
            print("good")
            consecutive_failures = 0
            savesong(detail_songs)

        except ValueError as error:
            print(error)
            consecutive_failures = 0
        except Exception as error:
            print(error)
            consecutive_failures += 1

        if consecutive_failures >= 3:
            print("连续请求失败，stop")
            break

        delay = random.uniform(3, 4)
        time.sleep(delay)
    return detail_songs


songs = playwrit()
print("ok")