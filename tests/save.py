from pathlib import Path
from playwright.sync_api import sync_playwright

auth_path = Path(".auth/kugou_state.json")

url = "https://www.kugou.com/mixsong/fh4ofz94.html"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.8.7271 SLBChan/115 SLBVPV/64-bit"
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(user_agent=user_agent)
    page = context.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=30000)

    input("enter")
    context.storage_state(path=auth_path)
    print("ok")
    browser.close()
# 记录登录状态
