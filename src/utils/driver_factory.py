"""
utils/driver_factory.py

Creates and configures WebDriver instances.
Works identically on Windows, macOS, Linux, and GitHub Actions CI.

ChromeDriver resolution order:
  1. CHROMEDRIVER_PATH env var — injected by CI (setup-chrome action)
  2. System chromedriver on PATH — set by: sudo apt install chromium-driver
  3. webdriver-manager — auto-download with THIRD_PARTY_NOTICES bug fix
"""

import glob
import os
import platform
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from src.config import settings


def create_driver() -> webdriver.Remote:
    """Return a fully configured WebDriver. Browser driven by BROWSER env var."""
    browser = settings.BROWSER
    if browser == "chrome":
        return _create_chrome_driver()
    elif browser == "firefox":
        return _create_firefox_driver()
    elif browser == "edge":
        return _create_edge_driver()
    else:
        raise ValueError(f"Unsupported browser: '{browser}'. Supported: chrome, firefox, edge")


def _resolve_chromedriver() -> str:
    """
    Find the chromedriver binary using a robust multi-strategy approach.

    Strategy 1 — CHROMEDRIVER_PATH env var (set by GitHub Actions setup-chrome).
    Strategy 2 — system chromedriver on PATH (apt install chromium-driver).
    Strategy 3 — webdriver-manager with THIRD_PARTY_NOTICES bug workaround.
    """
    # Strategy 1: CI injects the exact path via env var
    ci_path = os.environ.get("CHROMEDRIVER_PATH", "").strip()
    if ci_path and os.path.isfile(ci_path):
        print(f"[driver_factory] Using CI chromedriver: {ci_path}")
        return ci_path

    # Strategy 2: system chromedriver (most reliable on local Linux/Mac)
    system_path = shutil.which("chromedriver")
    if system_path:
        print(f"[driver_factory] Using system chromedriver: {system_path}")
        return system_path

    # Strategy 3: webdriver-manager with bug fix
    print("[driver_factory] Falling back to webdriver-manager...")
    wdm_path = ChromeDriverManager().install()

    if "THIRD_PARTY_NOTICES" not in wdm_path and os.path.isfile(wdm_path):
        return wdm_path

    # Fix the known wdm THIRD_PARTY_NOTICES bug — find real binary in same dir
    driver_dir = os.path.dirname(wdm_path)
    for candidate in sorted(glob.glob(os.path.join(driver_dir, "chromedriver*"))):
        if "THIRD_PARTY" not in candidate and os.path.isfile(candidate):
            os.chmod(candidate, 0o755)
            print(f"[driver_factory] Fixed wdm path: {candidate}")
            return candidate

    raise FileNotFoundError(
        "Could not locate chromedriver binary.\n"
        "Local fix:  sudo apt install -y chromium-driver\n"
        f"wdm returned: {wdm_path}"
    )


def _chrome_options() -> ChromeOptions:
    """Build Chrome options that work on all environments."""
    opts = ChromeOptions()

    if settings.HEADLESS:
        opts.add_argument("--headless=new")

    # Required for Linux CI (no display server, limited shared memory)
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--disable-default-apps")
    opts.add_argument("--remote-debugging-port=0")

    # Suppress automation banners and popups
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--disable-blink-features=AutomationControlled")

    return opts


def _create_chrome_driver() -> webdriver.Chrome:
    driver = webdriver.Chrome(
        service=ChromeService(_resolve_chromedriver()),
        options=_chrome_options(),
    )
    _configure(driver)
    return driver


def _create_firefox_driver() -> webdriver.Firefox:
    opts = FirefoxOptions()
    if settings.HEADLESS:
        opts.add_argument("--headless")
    opts.add_argument("--width=1920")
    opts.add_argument("--height=1080")

    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=opts,
    )
    _configure(driver)
    return driver


def _create_edge_driver() -> webdriver.Edge:
    opts = EdgeOptions()
    if settings.HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")

    driver = webdriver.Edge(
        service=EdgeService(EdgeChromiumDriverManager().install()),
        options=opts,
    )
    _configure(driver)
    return driver


def _configure(driver: webdriver.Remote) -> None:
    """Apply timeouts and window size uniformly across all browsers."""
    driver.implicitly_wait(settings.IMPLICIT_WAIT)
    driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
    driver.maximize_window()
