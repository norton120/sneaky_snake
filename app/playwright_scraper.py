from playwright.sync_api import sync_playwright
from contextlib import contextmanager
from typing import Optional, TYPE_CHECKING
import shutil
import os
from app.logger import logger

if TYPE_CHECKING:
    from playwright.sync_api import Browser, Page

class Scraper:
    browser: Optional["Browser"] = None
    page: Optional["Page"] = None

    def __init__(self, reset_profile: bool = False):
        logger.info(f"Initializing Scraper with reset_profile={reset_profile}")
        self.copy_profile(reset_profile)

    def copy_profile(self, reset_profile: bool = False):
        profile_path = "/data/.config/google-chrome"
        if os.path.exists(profile_path):
            if reset_profile:
                logger.info("Resetting Chrome profile")
                shutil.rmtree(profile_path)
            else:
                logger.debug("Using existing Chrome profile")
                return
        logger.info("Copying fresh Chrome profile")
        shutil.copytree("/root/google-chrome", profile_path)

    @contextmanager
    def launch_browser(self):
        logger.debug("Launching browser with persistent context")
        with sync_playwright() as p:
            try:
                self.browser = p.chromium.launch_persistent_context(
                    user_data_dir="/app/.config/google-chrome",
                    headless=False,
                    args=["--profile-directory=Default"]
                )
                logger.debug("Browser launched successfully")
                yield
            except Exception as e:
                logger.error(f"Error launching browser: {str(e)}", exc_info=True)
                raise
            finally:
                logger.debug("Closing browser")
                if self.browser:
                    self.browser.close()

    def raw_scrape(self, url: str) -> str:
        logger.info(f"Starting scrape of URL: {url}")
        with self.launch_browser():
            try:
                logger.debug("Creating new page")
                self.page = self.browser.new_page()
                logger.debug(f"Navigating to URL: {url}")
                self.page.goto(url)
                logger.debug("Waiting for page load")
                self.page.wait_for_load_state("load", timeout=10000)
                logger.debug("Getting page content")
                html_content = self.page.content()
                logger.info(f"Successfully scraped URL: {url}")
                return html_content
            except Exception as e:
                logger.error(f"Error scraping URL {url}: {str(e)}", exc_info=True)
                raise

