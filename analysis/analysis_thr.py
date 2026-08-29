from pathlib import Path
from collections import Counter
import json
import re
import jieba
import pandas

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

stop_words = ["作词","作曲","编曲","演唱","制作人","Producer",
                    "混音","录音","监制","发行","出品","母带","和声",
                    "吉他","贝斯","鼓手","版权","公司"]
not_words = {"我们", "你们", "他们","一个","一次","爱是"}


# 统计词语总出现次数
total_word_counts = Counter()
song_word_counts = Counter()


for idx, song in loved_song_data.iterrows():
    song_name = str(song["song_name"]).strip()
    rawlyrics = str(song["lyrics"])
    lyrics = []
    for line in rawlyrics.splitlines():
        if line != "":
            lyrics.append(line)
    clean_lines = []
    for line in lyrics:
        for word in stop_words:
            if word.lower() in line.lower():
                break
        else:
            clean_lines.append(line)
    clean_lyrics = "\n".join(clean_lines)


    words = jieba.lcut(clean_lyrics)
    valid_words = []

    for word in words:
        word = word.strip()

        if word == "":
            continue
        if word in not_words:
            continue
        if not re.fullmatch(r"[\u4e00-\u9fff]+",word):
            continue
        if len(word) < 2:
            continue
        valid_words.append(word)
    if len(valid_words) == 0:
        continue

    # 统计总出现次数
    total_word_counts.update(valid_words)
    song_word_counts.update(set(valid_words))

analysis_ans = []

for word, word_count in total_word_counts.most_common(30):
    song_count = song_word_counts[word]
    analysis_ans.append(
        {
            "word": word,
            "word_count": word_count,
            "song_count": song_count,
        }
    )


word_analysis = pandas.DataFrame(analysis_ans)


print("歌词词频前30：")
print(word_analysis.to_string(index=False,))