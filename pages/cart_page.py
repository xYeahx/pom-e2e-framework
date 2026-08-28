"""页面层：购物车页（FR-08）。"""
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class CartPage(BasePage):
    """购物车页：校验条目与数量、进入结算。"""

    page_title = (By.CSS_SELECTOR, ".title")
    cart_items = (By.CSS_SELECTOR, "div.cart_item")
    item_name = (By.CSS_SELECTOR, "div.inventory_item_name")
    item_quantity = (By.CSS_SELECTOR, "div.cart_quantity")
    checkout_button = (By.CSS_SELECTOR, "button#checkout")
    continue_shopping_button = (By.CSS_SELECTOR, "button#continue-shopping")
    remove_buttons = (By.CSS_SELECTOR, "button.cart_button")

    def _item_locator(self, product_name: str):
        return (
            By.XPATH,
            f"//div[contains(@class,'cart_item')]"
            f"[.//div[contains(@class,'inventory_item_name') and normalize-space(.)='{product_name}']]",
        )

    def get_item_names(self) -> list:
        """返回购物车内全部商品名称。"""
        return [el.text.strip() for el in self.find_elements(self.item_name)]

    def get_item_count(self) -> int:
        """返回购物车条目数。"""
        return len(self.find_elements(self.cart_items))

    def get_quantity(self, product_name: str) -> str:
        """返回指定商品的数量。"""
        quantity_locator = (
            By.XPATH,
            f"{self._item_locator(product_name)[1]}//div[contains(@class,'cart_quantity')]",
        )
        return self.get_text(quantity_locator)

    def click_checkout(self):
        """点击结算按钮。"""
        return self.click(self.checkout_button)

    def click_continue_shopping(self):
        """点击继续购物。"""
        return self.click(self.continue_shopping_button)
