"""页面层：订单确认页（FR-09）。"""
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class CheckoutOverviewPage(BasePage):
    """订单确认页：核对商品与金额、提交订单。"""

    page_title = (By.CSS_SELECTOR, ".title")
    item_name = (By.CSS_SELECTOR, "div.inventory_item_name")
    item_price = (By.CSS_SELECTOR, "div.inventory_item_price")
    summary_total = (By.CSS_SELECTOR, "div.summary_total_label")
    finish_button = (By.ID, "finish")
    cancel_button = (By.ID, "cancel")

    def get_item_names(self) -> list:
        """返回订单确认页商品名称列表。"""
        return [el.text.strip() for el in self.find_elements(self.item_name)]

    def get_total_text(self) -> str:
        """返回订单总金额文案。"""
        return self.get_text(self.summary_total)

    def click_finish(self):
        """提交订单。"""
        return self.click(self.finish_button)
