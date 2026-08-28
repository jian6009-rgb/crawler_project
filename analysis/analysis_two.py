from pathlib import Path
import json
import pandas
import math
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
SONG_DATA_PATH = ROOT / "data" / "songs.json"
ARTIST_DATA_PATH = ROOT / "data" / "artists.json"


def normalurl(url):
    return url.replace(
        "https://music.91q.com",
        "https://music.taihe.com"
    )
    
with SONG_DATA_PATH.open("r",encoding="utf-8") as savefile:
        songs = json.load(savefile)
song_data = pandas.DataFrame(songs)
song_data["normalized_url"] = song_data["song_url"].apply(normalurl)
cleaned_song_data = song_data.drop_duplicates(subset = "normalized_url")
loved_song_data = cleaned_song_data[cleaned_song_data["song_name"].str.contains("爱",na=False)]


artist_song_data = loved_song_data[["normalized_url","singer_urls"]].explode("singer_urls")
artist_song_data = artist_song_data.dropna(subset=["singer_urls"])# 删除没有歌手网址的数据
artist_song_data["normalized_artist_url"] = (artist_song_data["singer_urls"].apply(normalurl))


grouped_artist_data = artist_song_data.groupby("normalized_artist_url")
artist_song_counts = grouped_artist_data["normalized_url"].nunique().sort_values(ascending=False)

total_artist_count = len(artist_song_counts)
one_song_artist_count = (artist_song_counts == 1).sum() #只有1首歌曲的歌手数量
one_song_artist_ratio = (one_song_artist_count/total_artist_count)*100 #只有1首歌曲的歌手占比

total_song_count = artist_song_counts.sum() #歌曲总数

#排列歌手
sorted_artist_counts = artist_song_counts.sort_values(ascending=True)
cumulative_pa_ratio = (sorted_artist_counts.cumsum()/ total_song_count* 100).tolist()

cumulative_artist_ratio = []

for artist_number in range(1,total_artist_count + 1):
    artist_ratio = (artist_number/ total_artist_count* 100)
    cumulative_artist_ratio.append(artist_ratio)


cumulative_artist_ratio.insert(0,0)
cumulative_pa_ratio.insert(0,0)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
x = cumulative_artist_ratio
y = cumulative_pa_ratio
plt.plot(x,y,color="#74685a",linewidth=2,label="实际分布")


plt.plot([0, 100],[0, 100],color="#A6402C",linestyle="--",label="完全平均分布")


plt.title("歌名含“爱”的歌曲中歌手参与量的洛伦兹曲线")
plt.xlabel("累计歌手比例（%）")
plt.ylabel("累计歌曲参与量比例（%）")
plt.xlim(0,100)
plt.ylim(0,100)
plt.grid(axis="both",linestyle="--",alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()