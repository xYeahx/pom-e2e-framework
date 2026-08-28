"""Driver 管理：根据配置创建/退出 WebDriver，自动匹配浏览器驱动（FR-17）。"""
import os

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from common.logger import get_logger

logger = get_logger("driver")

_BROWSERS = {
    "chrome": "chrome",
    "edge": "edge",
    "firefox": "firefox",
}


def _is_env_headless() -> bool:
    """支持通过 HEADLESS=1 环境变量强制无头模式（便于 CI/验证）。"""
    return os.getenv("HEADLESS", "").strip().lower() in ("1", "true", "yes")


def _common_args(options, headless: bool, window_size: str) -> None:
    if headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={window_size}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--ignore-certificate-errors")


def _create_chrome(headless: bool, window_size: str) -> WebDriver:
    options = webdriver.ChromeOptions()
    _common_args(options, headless, window_size)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    try:
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager

        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    except Exception as exc:  # webdriver-manager 不可用时退回 Selenium Manager
        logger.warning("webdriver-manager 初始化失败(%s)，使用 Selenium Manager 自动管理驱动", exc)
        return webdriver.Chrome(options=options)


def _create_edge(headless: bool, window_size: str) -> WebDriver:
    options = webdriver.EdgeOptions()
    _common_args(options, headless, window_size)
    try:
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.microsoft import EdgeChromiumDriverManager

        return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    except Exception as exc:
        logger.warning("webdriver-manager 初始化失败(%s)，使用 Selenium Manager 自动管理驱动", exc)
        return webdriver.Edge(options=options)


def _create_firefox(headless: bool, window_size: str) -> WebDriver:
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    options.add_argument(f"--width={window_size.split(',')[0]}")
    options.add_argument(f"--height={window_size.split(',')[1]}")
    try:
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager

        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    except Exception as exc:
        logger.warning("webdriver-manager 初始化失败(%s)，使用 Selenium Manager 自动管理驱动", exc)
        return webdriver.Firefox(options=options)


def create_driver(
    browser: str = "chrome",
    headless: bool = False,
    window_size: str = "1920,1080",
    implicit_wait: int = 5,
) -> WebDriver:
    """按配置创建 WebDriver 实例。"""
    browser = (browser or "chrome").lower()
    if browser not in _BROWSERS:
        raise ValueError(f"不支持的浏览器: {browser}，可选: {list(_BROWSERS)}")

    headless = headless or _is_env_headless()
    factory = {
        "chrome": _create_chrome,
        "edge": _create_edge,
        "firefox": _create_firefox,
    }[browser]
    driver = factory(headless, window_size)
    driver.implicitly_wait(implicit_wait)
    logger.info("Driver 创建完成: %s (headless=%s)", browser, headless)
    return driver
