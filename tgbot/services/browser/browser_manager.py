""" Browser Manager definition """

from playwright.async_api import Browser, Playwright, async_playwright


class BrowserManager:
    def __init__(self):
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None

    async def get_browser(self) -> Browser:
        if not self.playwright:
            self.playwright = await async_playwright().start()

        if not self.browser:
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox"],
            )

        return self.browser

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


browser_manager = BrowserManager()
