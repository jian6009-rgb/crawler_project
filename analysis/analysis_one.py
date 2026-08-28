from pathlib import Path
import json
import pandas
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
grouped_song_data = loved_song_data.groupby("song_name")  #从DataFrame转换成DataFrameGroupby
repeated_name_count = grouped_song_data.size().sort_values(ascending = False) #从DataFramegroupby转换成Series


name_analysis = repeated_name_count.reset_index(name="record_count") # 从Series转换成DataFrame
name_analysis["name_length"] = (name_analysis["song_name"].str.strip().str.len())
name_analysis["repeated_state"] = (name_analysis["record_count"] > 1)
name_analysis["name_length_group"] = pandas.cut(name_analysis["name_length"],
                                         bins=[0,2,4,6,8,float("inf")],
                                        labels = ["1-2字","3-4字","5-6字","7-8字","9字以上"])
length_groups = name_analysis.groupby("name_length_group",observed=False)
total_name_count = length_groups.size()
repeated_count = (length_groups["repeated_state"].sum())
length_analysis = pandas.DataFrame({"total_name_count": total_name_count,"repeated_count": repeated_count})
length_analysis["repeated_ratio (%)"] = (length_analysis["repeated_count"]/ length_analysis["total_name_count"]* 100)
print(length_analysis)



plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
x = length_analysis.index
y = length_analysis["repeated_ratio (%)"]
bars = plt.bar(x,y,color="#74685a")
bar_labels = []
for length_name in length_analysis.index:
    repeated_count = length_analysis.loc[
        length_name,
        "repeated_count"
    ]
    total_count = length_analysis.loc[
        length_name,
        "total_name_count"
    ]
    ratio = length_analysis.loc[
        length_name,
        "repeated_ratio (%)"
    ]
    label = (f"{ratio:.2f}%({repeated_count}/{total_count})")
    bar_labels.append(label)
    
plt.bar_label(bars,labels=bar_labels,padding=2)
plt.title("以“爱”作歌名的歌曲中长度与同名率的关系")
plt.xlabel("歌名长度组别")
plt.ylabel("歌名重复率")
plt.ylim( 0,length_analysis["repeated_ratio (%)"].max() + 10)
plt.grid( axis="both", linestyle="--", alpha=0.5 )
plt.tight_layout()
plt.show()