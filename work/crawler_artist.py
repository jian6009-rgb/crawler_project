from urllib.parse import urljoin
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
import re
import random
import time
from playwright.sync_api import sync_playwright

#新增一些注释：由于Kugou一直有一些防止爬虫的东西，因此改用qianqian音乐，crawler_song.py是几乎复制crawler_kugo.py，可在那里找到原代码,而这个是复制crawler_song.py
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.8.7271 SLBChan/115 SLBVPV/64-bit"
SONG_DATA_PATH = Path("data/songs.json")
ARTIST_DATA_PATH = Path("data/artists.json")

#写完这个代码后的小心思：其实这个代码能优化，如果把crawler_song.py和crawler_artist.py结合应该能让代码效率更高，更好。但是我当时心想一步一步来会更适合初学者，但结果让代码更复杂了。
#原本可以先找遍历歌手，进歌手网站然后把歌手简介和歌全一次性爬出来。
#但结果现在是先找歌曲写json，然后再json记录里找歌手，复杂了很多。而且我找歌曲2000首后发现其中有简介的歌手还没有100个，结果就是最后又要找多几个榜单录歌，再从json记录里找歌手。所以json歌曲不止2000首。



def getartist_sources(): #从json遍历歌曲，提取歌手url。并把信息制成字典：{歌手：歌曲s}
    with SONG_DATA_PATH.open("r",encoding="utf-8") as savefile:
        songs = json.load(savefile)

    artist_sources = {}

    for song in songs:
        singer_urls = song.get("singer_urls",[]) #其实也可写singer_urls = song["singer_urls"],但我没心思看json2000首歌是不是每个都有singer_urls。
        for singer_url in singer_urls:
            if not singer_url:
                continue

            song_data = {"song_name": song["song_name"],"song_url": song["song_url"]}
            if singer_url not in artist_sources:
                artist_sources[singer_url] = {"songs": [song_data]}
            else:
                if (song_data not in artist_sources[singer_url]["songs"]):
                    artist_sources[singer_url]["songs"].append(song_data)
                    
    return artist_sources


def getartist_detail(page,artist_url,artist_source): #在page上打开歌手url，在里面用locator找歌手信息组成字典。如果图片简介任一没有，则跳过
    
    page.goto(artist_url,wait_until="domcontentloaded",timeout=30000) #page写在这里是因为page可以有很多
    page.wait_for_selector(".info-box .info h1",timeout=15000)
    page.wait_for_timeout(2000) #等网站自己的运行，不然image_tag会变默认图片

    artist_name = page.locator(".info-box .info h1").inner_text().strip() #从源代码html自己慢慢找的
    if not artist_name:
        print("没有名")
        return None

    image_tag = page.locator(".info-box .avatar img") 
    if image_tag.count() == 0:
        print("没有图")
        return None

    artist_image_url = image_tag.first.get_attribute("src") #qianqian有可能会给歌手默认图片，所以要判断两次图片
    if (not artist_image_url or "user_pic" in artist_image_url or not artist_image_url.startswith("http")):
        print("没有歌手图")
        return None

    intro_tag = page.locator(".info-box .intro > div")

    if intro_tag.count() == 0:
        print("没有简介")
        return None

    artist_intro = intro_tag.first.inner_text().strip()
    if len(artist_intro) < 10: #没有简介的歌手直接抛弃
        print("没有简介")
        return None

    artist = {"artist_name": artist_name,"artist_image_url": artist_image_url,"artist_intro": artist_intro,"artist_url": artist_url,"songs": artist_source["songs"]}
    return artist


def saveartist(artists):

    with ARTIST_DATA_PATH.open("w",encoding="utf-8") as savefile:
        json.dump(artists,savefile,ensure_ascii=False,indent=2)

def playwrit(): #先getartist_sources()获取歌手名单，
    artist_sources = getartist_sources()




    
    if ARTIST_DATA_PATH.exists(): #打开歌手json，先把已记录歌手名单提取以实现断点续爬（用url和name分别查重进行双重保险，因为试过只用url查重的话，金莎一个歌手录了两次）
        with ARTIST_DATA_PATH.open("r",encoding="utf-8") as savefile:
            detail_artists = json.load(savefile)
    else:
        detail_artists = []

    saved_artist_urls = []
    saved_artist_names = []
    
    for saved_artist in detail_artists:
        saved_artist_urls.append(saved_artist["artist_url"])
        saved_artist_names.append(saved_artist["artist_name"])




        

    with sync_playwright() as playwright: #打开context,对歌手名单每个歌手进行getartist_detail(),然后saveartist()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()

        for idx, artist_data in enumerate(artist_sources.items(),start=1): #给列表每个歌手做一次getartist_detail，最后保存

            artist_url = artist_data[0]
            artist_source = artist_data[1]
            if artist_url in saved_artist_urls:
                continue
            try:
                detail_artist = getartist_detail(page,artist_url,artist_source)

                if detail_artist is None:
                    print ("no")
                elif detail_artist["artist_name"] in saved_artist_names: #不对同一个歌手重复进行
                    print ("no")
                else:
                    detail_artists.append(detail_artist)
                    saved_artist_urls.append(artist_url)
                    saved_artist_names.append(detail_artist["artist_name"])
                    saveartist(detail_artists)

            except Exception as error:
                print(error)

            delay = random.uniform(2, 3)
            time.sleep(delay)
        browser.close()
    return detail_artists

artists = playwrit()
print("ok")