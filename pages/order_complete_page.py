"""页面层：下单成功页（FR-09）。"""
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class OrderCompletePage(BasePage):
    """下单成功页：校验订单提交结果。"""

    complete_header = (By.CSS_SELECTOR, "h2.complete-header")
    complete_text = (By.CSS_SELECTOR, "div.complete-text")
    back_home_button = (By.ID, "back-to-products")

    def get_complete_header(self) -> str:
        """返回成功页主标题文案。"""
        return self.get_text(self.complete_header)

    def get_complete_text(self) -> str:
        """返回成功页描述文案。"""
        return self.get_text(self.complete_text)

    def is_order_success(self) -> bool:
        """校验下单成功：成功页标题出现且包含感谢文案。"""
        return self.is_visible(self.complete_header, timeout=10) and "Thank you" in self.get_complete_header()
