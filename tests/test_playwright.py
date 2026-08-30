from pathlib import Path
from playwright.sync_api import sync_playwright

url = "https://www.kugou.com/mixsong/fh4ofz94.html"  # 用的是第一首歌
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.8.7271 SLBChan/115 SLBVPV/64-bit"
auth_path = Path(
    ".auth/kugou_state.json"
)  # 用来自动登录，因为酷狗一定要登录才有歌词 （用context.storage_state()，在自己手动登陆时，记录cookie

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(user_agent=user_agent, storage_state=str(auth_path))
    page = context.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=30000)

    page.wait_for_function(
        """
        () => {
            const element =
                document.querySelector(".songWordContent");

            return element &&
                   element.innerText.trim().length > 0;
        }
        """,
        timeout=15000,
    )  # javascript

    # get_attribute获取属性，inner_text是文本
    cover_url = page.locator(".albumImg img").get_attribute("src")
    lyrics = page.locator(".songWordContent").inner_text().strip()
    singer_tag = page.locator(".songDetail .singerName a")
    singer_name = singer_tag.inner_text().strip()
    singer_url = singer_tag.get_attribute("href")

    print("封面图片：", cover_url)
    print(lyrics[:500])
    print("歌手名字：", singer_name)
    print("歌手url：", repr(singer_url))
    input("enter")
    browser.close()
