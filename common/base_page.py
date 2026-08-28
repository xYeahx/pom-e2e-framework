"""BasePage 基类（FR-04）：封装元素定位、显性等待、点击输入、滚动、截图等公共能力。

定位器格式支持两种：
- 单一主定位：        (By.ID, "user-name")
- 多级备选定位（FR-14）：[(By.ID, "login-button"), (By.CSS_SELECTOR, "input[data-test='login-button']")]
"""
from datetime import datetime
from typing import Callable, List, Optional, Sequence, Tuple, Union

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from common.config_loader import get_config, project_root
from common.logger import get_logger

# 定位器类型：单一定位 (By, value) 或多级备选定位 [(By, value), ...]
Locator = Union[Tuple[str, str], Sequence[Tuple[str, str]]]


class BasePage:
    """所有页面类的基类，提供页面通用操作能力。"""

    def __init__(self, driver: WebDriver, timeout: Optional[float] = None):
        self.driver = driver
        cfg = get_config()
        timeouts = cfg.get("timeout", {})
        self.timeout = timeout or timeouts.get("normal", 10)
        self.poll_frequency = timeouts.get("poll_frequency", 0.5)
        self.short_timeout = timeouts.get("short", 5)
        self.long_timeout = timeouts.get("long", 30)
        self.logger = get_logger(self.__class__.__name__)

    # ---------- 定位 ----------

    def _split_locators(self, locator: Locator) -> List[Tuple[str, str]]:
        """将单一定位/备选定位统一拆分为列表。"""
        if isinstance(locator, (tuple, list)) and len(locator) == 2 and isinstance(locator[0], str):
            return [locator]
        return list(locator)

    # ---------- 显性等待（FR-11） ----------

    def _wait(self, timeout: Optional[float]) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout or self.timeout, self.poll_frequency)

    def wait_until_visible(self, locator: Locator, timeout: Optional[float] = None) -> WebElement:
        """等待元素可见（visibility_of_element_located）。"""
        locators = self._split_locators(locator)
        if len(locators) == 1:
            return self._wait(timeout).until(ec.visibility_of_element_located(locators[0]))
        return self._wait(timeout).until(ec.any_of(*[ec.visibility_of_element_located(l) for l in locators]))

    def wait_until_clickable(self, locator: Locator, timeout: Optional[float] = None) -> WebElement:
        """等待元素可点击（element_to_be_clickable）。"""
        locators = self._split_locators(locator)
        if len(locators) == 1:
            return self._wait(timeout).until(ec.element_to_be_clickable(locators[0]))
        return self._wait(timeout).until(ec.any_of(*[ec.element_to_be_clickable(l) for l in locators]))

    def wait_until_present(self, locator: Locator, timeout: Optional[float] = None) -> WebElement:
        """等待元素出现在 DOM（presence_of_element_located）。"""
        locators = self._split_locators(locator)
        if len(locators) == 1:
            return self._wait(timeout).until(ec.presence_of_element_located(locators[0]))
        return self._wait(timeout).until(ec.any_of(*[ec.presence_of_element_located(l) for l in locators]))

    def wait_until_gone(self, locator: Locator, timeout: Optional[float] = None):
        """等待元素消失（invisibility_of_element_located，用于 loading 等）。"""
        locators = self._split_locators(locator)
        if len(locators) == 1:
            return self._wait(timeout).until(ec.invisibility_of_element_located(locators[0]))
        return self._wait(timeout).until(ec.all_of(*[ec.invisibility_of_element_located(l) for l in locators]))

    def wait_until_text(self, locator: Locator, text: str, timeout: Optional[float] = None):
        """等待元素出现指定文本（text_to_be_present_in_element）。"""
        locators = self._split_locators(locator)
        if len(locators) == 1:
            return self._wait(timeout).until(ec.text_to_be_present_in_element(locators[0], text))
        return self._wait(timeout).until(ec.any_of(*[ec.text_to_be_present_in_element(l, text) for l in locators]))

    def wait_until(self, condition: Callable[[WebDriver], bool], description: str = "", timeout: Optional[float] = None):
        """通用显性等待：自定义条件。"""
        return self._wait(timeout).until(condition, message=description)

    def wait_loading_done(self, loading_locator: Locator, timeout: Optional[float] = None):
        """等待异步 loading 指示器消失（FR-12）。"""
        try:
            self.wait_until_gone(loading_locator, timeout or self.long_timeout)
            self.logger.info("异步加载完成（loading 消失）: %s", loading_locator)
        except TimeoutException:
            self.logger.warning("loading 元素未在预期时间内消失: %s", loading_locator)

    # ---------- 查找 ----------

    def find_element(self, locator: Locator, timeout: Optional[float] = None) -> WebElement:
        """按主定位 + 备选定位策略查找元素，返回第一个匹配元素（FR-14）。"""
        locators = self._split_locators(locator)
        last_exc = None
        for single in locators:
            try:
                element = self._wait(timeout).until(ec.presence_of_element_located(single))
                if len(locators) > 1:
                    self.logger.info("主定位失效，备选定位生效: %s", single)
                return element
            except TimeoutException as exc:
                last_exc = exc
        raise last_exc or NoSuchElementException(f"全部定位策略均失败: {locator}")

    def find_elements(self, locator: Locator, timeout: Optional[float] = None) -> List[WebElement]:
        """等待至少一个元素出现后返回全部匹配元素列表。"""
        locators = self._split_locators(locator)
        self._wait(timeout).until(ec.presence_of_element_located(locators[0]))
        return self.driver.find_elements(*locators[0])

    # ---------- 页面操作 ----------

    def click(self, locator: Locator, timeout: Optional[float] = None, js_fallback: bool = True) -> WebElement:
        """点击元素：等待可点击；被遮挡时降级为 JS 点击（FR-13 遮挡处理）。"""
        element = self.wait_until_clickable(locator, timeout)
        try:
            element.click()
        except (ElementClickInterceptedException, ElementNotInteractableException) as exc:
            if not js_fallback:
                raise
            self.logger.warning("元素点击被遮挡(%s)，改用 JS 点击: %s", exc, locator)
            self.driver.execute_script("arguments[0].click();", element)
        self.logger.info("点击元素: %s", locator)
        return element

    def click_js(self, locator: Locator, timeout: Optional[float] = None) -> WebElement:
        """直接使用 JS 点击元素。"""
        element = self.wait_until_present(locator, timeout)
        self.driver.execute_script("arguments[0].click();", element)
        self.logger.info("JS 点击元素: %s", locator)
        return element

    def input_text(self, locator: Locator, text: str, timeout: Optional[float] = None, clear: bool = True) -> WebElement:
        """输入文本：等待可见后清空再输入。"""
        element = self.wait_until_visible(locator, timeout)
        if clear:
            element.clear()
        element.send_keys(text)
        self.logger.info("输入文本: %s <- %s", locator, text)
        return element

    def get_text(self, locator: Locator, timeout: Optional[float] = None) -> str:
        """获取元素文本（去首尾空白）。"""
        element = self.wait_until_visible(locator, timeout)
        return element.text.strip()

    def get_attribute(self, locator: Locator, attribute: str, timeout: Optional[float] = None) -> str:
        """获取元素属性值。"""
        element = self.wait_until_present(locator, timeout)
        return element.get_attribute(attribute)

    def is_visible(self, locator: Locator, timeout: Optional[float] = None) -> bool:
        """判断元素是否可见（不抛异常）。"""
        try:
            self.wait_until_visible(locator, timeout or self.short_timeout)
            return True
        except TimeoutException:
            return False

    def is_present(self, locator: Locator, timeout: Optional[float] = None) -> bool:
        """判断元素是否存在于 DOM（不抛异常）。"""
        try:
            self.wait_until_present(locator, timeout or self.short_timeout)
            return True
        except TimeoutException:
            return False

    def scroll_into_view(self, locator: Locator, timeout: Optional[float] = None) -> WebElement:
        """滚动至元素可见位置。"""
        element = self.wait_until_present(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.logger.info("滚动至元素: %s", locator)
        return element

    def scroll_to_top(self) -> None:
        """滚动回页面顶部。"""
        self.driver.execute_script("window.scrollTo(0, 0);")

    def select_option_by_text(self, locator: Locator, text: str, timeout: Optional[float] = None) -> None:
        """下拉框按可见文本选择。"""
        element = self.wait_until_present(locator, timeout)
        Select(element).select_by_visible_text(text)
        self.logger.info("下拉选择: %s -> %s", locator, text)

    def handle_popups(self, popup_locators: Optional[list] = None) -> int:
        """处理弹窗遮挡（FR-13）：按配置关闭 cookie/广告等弹窗，失败不影响主流程。"""
        cfg = get_config()
        popups = popup_locators if popup_locators is not None else cfg.get("popups", [])
        handled = 0
        for popup in popups:
            close_btn = popup.get("close")
            if not close_btn:
                continue
            try:
                if self.is_visible(close_btn, timeout=1):
                    self.click(close_btn, timeout=1)
                    self.logger.info("已关闭弹窗: %s", close_btn)
                    handled += 1
            except Exception as exc:
                self.logger.debug("弹窗处理跳过: %s", exc)
        return handled

    # ---------- 截图（FR-15） ----------

    def screenshot(self, name: str) -> str:
        """保存截图至 screenshots/ 目录，命名含场景名与时间戳。"""
        cfg = get_config()
        shots_dir = project_root() / cfg.get("directories", {}).get("screenshots", "screenshots")
        shots_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = shots_dir / f"{name}_{timestamp}.png"
        self.driver.save_screenshot(str(path))
        self.logger.info("截图已保存: %s", path)
        return str(path)
