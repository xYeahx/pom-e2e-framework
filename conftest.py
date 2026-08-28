"""pytest 全局配置：Driver 生命周期、公共 fixture、失败截图钩子（FR-15/FR-20）。"""
from datetime import datetime

import pytest

from common.config_loader import get_config, project_root
from common.driver_manager import create_driver
from common.logger import get_logger

logger = get_logger("conftest")


@pytest.fixture(scope="session")
def config() -> dict:
    """全局配置。"""
    return get_config()


@pytest.fixture(scope="session")
def base_url(config) -> str:
    """被测站点基础 URL。"""
    return config["url"]["base"].rstrip("/")


@pytest.fixture(scope="function")
def driver(config) -> None:
    """每个用例独立的 WebDriver 实例，用例结束后自动退出。"""
    browser_cfg = config["browser"]
    d = create_driver(
        browser=browser_cfg.get("name", "chrome"),
        headless=browser_cfg.get("headless", False),
        window_size=browser_cfg.get("window_size", "1920,1080"),
        implicit_wait=config.get("timeout", {}).get("implicit_wait", 5),
    )
    yield d
    try:
        d.quit()
    except Exception:
        pass


def pytest_configure(config: "pytest.Config"):
    """确保报告目录存在。"""
    reports_dir = project_root() / get_config()["directories"]["reports"]
    reports_dir.mkdir(parents=True, exist_ok=True)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时自动截图（FR-15），并附加到 HTML 报告。"""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    try:
        driver_instance = item.funcargs.get("driver")
        if driver_instance is None:
            return
        shots_dir = project_root() / get_config()["directories"]["screenshots"]
        shots_dir.mkdir(parents=True, exist_ok=True)
        name = f"{item.name}_{datetime.now():%Y%m%d_%H%M%S}"
        path = shots_dir / f"{name}.png"
        driver_instance.save_screenshot(str(path))
        logger.error("用例失败，截图已保存: %s", path)
        try:
            from pytest_html import extras

            report.extras = getattr(report, "extras", []) + [extras.png(str(path))]
        except Exception:
            pass
    except Exception:
        logger.debug("失败截图生成失败（Driver 可能已退出）", exc_info=True)
