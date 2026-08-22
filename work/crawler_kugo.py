from pathlib import Path
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import re
import random
import time

#需要的信息总结（暂时是榜单1）后面要遍历榜单
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.8.7271 SLBChan/115 SLBVPV/64-bit"
AUTH_PATH = Path(".auth/kugou_state.json")
HEADERS = {"User-Agent": USER_AGENT}
DATA_PATH = Path("data/songs.json")

def create_urllist(head,tail):
    url_list = []
    for page_num in range(head,tail+1):
        url = ("https://www.kugou.com/yy/rank/home/" f"{page_num}-8888.html?from=rank")
        url_list.append(url)
    return url_list


def getrank_songs(rank_url): #复制的crawler.ipynb 在那里有原文档可以复制
    response = requests.get(rank_url,headers=HEADERS,timeout=10)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    song_tags = soup.select(".pc_temp_songlist li")
    songs = []
    for song_tag in song_tags:
        link_tag = song_tag.select_one("a.pc_temp_songname") #找到有pc_temp_songname的a
        full_title = song_tag.get("title") #select 找文字，get 找属性
        singer_name, song_name = full_title.split(" - ", 1) #title格式：万海东 - 山风山风等等我
        song_url = link_tag.get("href")
        song = {"song_name": song_name,"singer_name": singer_name,"song_url": song_url}
        songs.append(song)
        delay = random.uniform(0.5, 1)
        time.sleep(delay)
    return songs


    
def getsong_detail(page, song):   #复制的crawler.ipynb 在那里有原文档可以复制
    page.goto(song["song_url"],wait_until="domcontentloaded",timeout=30000)
    page.wait_for_function(
        """
        () => {
            const element =
                document.querySelector(".songWordContent");

            return element &&
                   element.innerText.trim().length > 0;
        }
        """,
        timeout=30000
    )
    cover_url = page.locator(".albumImg img").get_attribute("src")
    rawlyrics = page.locator(".songWordContent").inner_text().strip()
    lyrics = re.sub(r"\A.*?』\s*","",rawlyrics,flags=re.DOTALL).strip()
    singer_tags = page.locator(".songDetail .singerName a") 
    singer_names = []#用列表是因为怕有多位歌手
    singer_urls = []
    for index in range(singer_tags.count()):
        singer_tag = singer_tags.nth(index)
        singer_name = singer_tag.inner_text().strip()
        singer_url = singer_tag.get_attribute("href")
        singer_names.append(singer_name)
        singer_urls.append(singer_url)

    
    song["cover_url"] = cover_url
    song["lyrics"] = lyrics
    song["detail_singer_names"] = singer_names
    song["singer_urls"] = singer_urls
    return song

def savesong(songs):
    with DATA_PATH.open("w",encoding="utf-8") as savefile:
        json.dump(songs,savefile,ensure_ascii=False,indent=2)


def show_failed_response(response):
    if response.status >= 400:
        print("请求异常：",response.status,response.url)

        
def playwrit():  #复制的crawler.ipynb 在那里有原文档可以复制
    songs = []
    for url in create_urllist(1,1):
        songs.extend(getrank_songs(url))
    detail_songs = []
    consecutive_failures = 0
    
    with sync_playwright() as playwright: 
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT ,storage_state=str(AUTH_PATH))
        page = context.new_page()
        page.on("response",show_failed_response)

        for idx, song in enumerate(songs, start = 1):
            print(f"{idx}:{song['song_name']}")
            try:
                detail_song = getsong_detail(page, song)
                detail_song["status"] = "success"
                detail_songs.append(detail_song)
                print("good")
                consecutive_failures = 0
                savesong(detail_songs)
            except Exception as error:
                print(error)
                consecutive_failures += 1
            if consecutive_failures >= 3:
                print("连续3首没有成功，停止")
                break
            delay = random.uniform(3, 4)
            time.sleep(delay)
        browser.close()
    return detail_songs

songs = playwrit()
print("ok")