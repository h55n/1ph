from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto("https://lu.ma/explore", timeout=30000, wait_until="domcontentloaded")
        print(page.title())
        page.screenshot(path="luma_explore.png")
        print("Done")

test()
