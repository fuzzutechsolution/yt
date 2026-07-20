"""
Universal AI Web Scraper - Scraping Engine Module
Orchestrates Selenium WebDrivers, respects robots.txt permissions,
executes tasks in the background, handles retries, timeouts, and reports progress.
"""

import time
import logging
import requests
import threading
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from typing import Callable, Dict, Any, List, Optional

# Selenium Web Driver Imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import WebDriverException, TimeoutException

# Local modules
from database import DatabaseManager
from parser import AIHtmlParser

logger = logging.getLogger(__name__)

# Standard User-Agent lists to alternate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

class ScrapingTask:
    """
    Encapsulates the state and execution logic for a single scraping request.
    Runs inside a background thread to prevent UI freezing.
    """
    def __init__(
        self,
        url: str,
        prompt: str,
        settings: Dict[str, str],
        on_progress: Callable[[float, str], None],
        on_success: Callable[[List[Dict[str, Any]], str], None],
        on_failure: Callable[[str], None],
        history_id: int
    ):
        self.url = url
        self.prompt = prompt
        self.settings = settings
        self.on_progress = on_progress
        self.on_success = on_success
        self.on_failure = on_failure
        self.history_id = history_id
        
        self.driver: Optional[webdriver.Remote] = None
        self._is_cancelled = False
        self._db = DatabaseManager.get_instance()

    def cancel(self):
        """Cancels execution and closes WebDriver immediately."""
        self._is_cancelled = True
        logger.info("Scraping task cancellation requested.")
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver quit successfully during cancellation.")
            except Exception as e:
                logger.debug(f"Failed to quit driver during cancellation: {e}")

    def execute(self):
        """Executes the scraping lifecycle with safety retries and robots.txt check."""
        # 1. Validate URL format
        parsed_url = urlparse(self.url)
        if not parsed_url.scheme or not parsed_url.netloc:
            self.on_failure("Invalid URL: Please make sure the URL contains http:// or https://")
            self._db.update_history_status(self.history_id, "FAILED")
            return

        # 2. robots.txt Verification
        self.on_progress(0.1, "Checking website robots.txt policies...")
        if not self._check_robots_txt(parsed_url):
            self.on_failure("Scraping blocked by target website's robots.txt policies.")
            self._db.update_history_status(self.history_id, "FAILED")
            return

        if self._is_cancelled:
            self._db.update_history_status(self.history_id, "CANCELLED")
            return

        # 3. Retrieve settings
        browser_type = self.settings.get("browser", "Chrome")
        headless = self.settings.get("headless", "True").lower() == "true"
        timeout = int(self.settings.get("timeout", "30"))
        max_retries = int(self.settings.get("retry_count", "3"))

        driver_created = False
        retry_count = 0
        
        while retry_count < max_retries and not driver_created:
            if self._is_cancelled:
                self._db.update_history_status(self.history_id, "CANCELLED")
                return

            try:
                retry_count += 1
                msg = f"Initializing {browser_type} driver (Attempt {retry_count}/{max_retries})..."
                self.on_progress(0.2, msg)
                logger.info(msg)

                self.driver = self._init_webdriver(browser_type, headless, timeout)
                driver_created = True
            except Exception as e:
                err_msg = str(e)
                logger.error(f"Failed to initialize webdriver: {err_msg}")
                if retry_count >= max_retries:
                    self.on_failure(f"Browser Driver Initialization Failure: {err_msg}\n"
                                    "Please check if browser is installed or update settings.")
                    self._db.update_history_status(self.history_id, "FAILED")
                    return
                time.sleep(2)

        # 4. Load Target Page
        self.on_progress(0.4, f"Navigating to {self.url}...")
        try:
            self.driver.set_page_load_timeout(timeout)
            self.driver.get(self.url)
            
            # Wait short time for dynamic content loading/rendering
            self.on_progress(0.6, "Waiting for JS scripts to complete rendering...")
            time.sleep(3)
        except TimeoutException:
            logger.warning("Page load timed out. Continuing with partially loaded HTML.")
            self.on_progress(0.7, "Page load timeout reached. Processing partial DOM content...")
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            self.on_failure(f"Navigation Failure: Could not reach host. Error: {str(e)}")
            self._close_driver()
            self._db.update_history_status(self.history_id, "FAILED")
            return

        if self._is_cancelled:
            self._close_driver()
            self._db.update_history_status(self.history_id, "CANCELLED")
            return

        # 5. Extract Page Content & Parse
        self.on_progress(0.8, "Extracting DOM and running AI-assisted parsing...")
        try:
            html_content = self.driver.page_source
            parser = AIHtmlParser(self.url)
            results, parser_explanation = parser.parse(html_content, self.prompt)
            
            self._close_driver()
            
            if self._is_cancelled:
                self._db.update_history_status(self.history_id, "CANCELLED")
                return

            # Save results to DB
            if results:
                self.on_progress(0.95, f"Saving {len(results)} extracted items to database...")
                self._db.save_results(self.history_id, results)
                self._db.update_history_status(self.history_id, "COMPLETED", count=len(results))
                logger.info(f"Scrape completed. Saved {len(results)} items.")
                self.on_success(results, parser_explanation)
            else:
                self._db.update_history_status(self.history_id, "COMPLETED", count=0)
                self.on_success([], "No structured data could be extracted based on your instructions. Try refining your prompt.")
                
        except Exception as e:
            logger.error(f"Parsing error: {e}", exc_info=True)
            self.on_failure(f"Parsing Error: {str(e)}")
            self._close_driver()
            self._db.update_history_status(self.history_id, "FAILED")

    def _check_robots_txt(self, parsed_url) -> bool:
        """
        Respects robots.txt rules. Warns the user but runs scraper 
        if override or implicit permissions are permitted.
        """
        try:
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            
            # Use requests with a timeout to fetch robots.txt quickly
            headers = {"User-Agent": USER_AGENTS[0]}
            resp = requests.get(robots_url, headers=headers, timeout=5)
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
                # Check permission for default user-agent
                allowed = rp.can_fetch("*", self.url)
                logger.info(f"robots.txt permission query result for '*': {allowed}")
                return allowed
            elif resp.status_code == 404:
                # No robots.txt, default is allowed
                return True
            # Let it pass if we can't load the robots.txt explicitly, but log it
            logger.warning(f"Could not retrieve robots.txt status ({resp.status_code}). Proceeding with caution.")
            return True
        except Exception as e:
            logger.warning(f"Failed to check robots.txt: {e}. Defaulting to allowed.")
            return True

    def _init_webdriver(self, browser_type: str, headless: bool, timeout: int) -> webdriver.Remote:
        """Configures options and driver service for Chrome, Firefox, or Edge."""
        import random
        user_agent = random.choice(USER_AGENTS)

        if browser_type.lower() == "chrome":
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            opts = ChromeOptions()
            if headless:
                opts.add_argument("--headless=new")
            opts.add_argument(f"user-agent={user_agent}")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            # Selenium 4 Manager handles finding/downloading webdriver binary automatically
            driver = webdriver.Chrome(options=opts)
            return driver

        elif browser_type.lower() == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            opts = FirefoxOptions()
            if headless:
                opts.add_argument("-headless")
            opts.set_preference("general.useragent.override", user_agent)
            driver = webdriver.Firefox(options=opts)
            return driver

        elif browser_type.lower() == "edge":
            from selenium.webdriver.edge.options import Options as EdgeOptions
            opts = EdgeOptions()
            if headless:
                opts.add_argument("--headless=new")
            opts.add_argument(f"user-agent={user_agent}")
            driver = webdriver.Edge(options=opts)
            return driver

        else:
            raise ValueError(f"Browser type '{browser_type}' is not supported. Use Chrome, Firefox, or Edge.")

    def _close_driver(self):
        """Safely shuts down the active Selenium webdriver session."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None


class ScrapingEngine:
    """
    Main manager for running background scraper tasks.
    Maintains a reference to the active task to allow cancellation.
    """
    def __init__(self):
        self.active_task: Optional[ScrapingTask] = None
        self._lock = threading.Lock()

    def start_scrape(
        self,
        url: str,
        prompt: str,
        settings: Dict[str, str],
        on_progress: Callable[[float, str], None],
        on_success: Callable[[List[Dict[str, Any]], str], None],
        on_failure: Callable[[str], None]
    ) -> bool:
        """
        Spawns a new background thread to execute the scraping work.
        Returns False if a task is already running.
        """
        with self._lock:
            if self.active_task is not None and self.active_task.driver is not None:
                logger.warning("Scraping already in progress. Cannot start a new task.")
                return False

            # Log to DB History first to get history ID
            db = DatabaseManager.get_instance()
            now_str = time.strftime('%Y-%m-%d %H:%M:%S')
            history_id = db.add_history_entry(url, prompt, now_str, "RUNNING")

            self.active_task = ScrapingTask(
                url=url,
                prompt=prompt,
                settings=settings,
                on_progress=on_progress,
                on_success=on_success,
                on_failure=on_failure,
                history_id=history_id
            )

        def worker():
            try:
                self.active_task.execute()
            except Exception as e:
                logger.error(f"Fatal crash inside scraping thread: {e}", exc_info=True)
                on_failure(f"Internal Scraping Thread Error: {str(e)}")
            finally:
                with self._lock:
                    self.active_task = None

        thread = threading.Thread(target=worker, name="ScrapingWorkerThread")
        thread.daemon = True
        thread.start()
        return True

    def stop_active_scrape(self):
        """Signals the current task to cancel immediately."""
        with self._lock:
            if self.active_task:
                self.active_task.cancel()
                self.active_task = None
