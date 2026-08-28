"""页面层：商品详情页（FR-07）。"""
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class ProductDetailPage(BasePage):
    """商品详情页：确认商品、加购。"""

    product_name = (By.CSS_SELECTOR, ".inventory_details_name")
    add_to_cart_button = (By.CSS_SELECTOR, "button#add-to-cart")
    back_button = (By.CSS_SELECTOR, "button#back-to-products")
    cart_badge = (By.CSS_SELECTOR, "span.shopping_cart_badge")

    def get_product_name(self) -> str:
        """获取详情页商品名称。"""
        return self.get_text(self.product_name)

    def click_add_to_cart(self):
        """点击加购按钮。"""
        return self.click(self.add_to_cart_button)

    def get_cart_count(self) -> int:
        """获取购物车角标数量。"""
        if not self.is_present(self.cart_badge, timeout=1):
            return 0
        return int(self.get_text(self.cart_badge))

    def go_back(self):
        """返回商品列表。"""
        return self.click(self.back_button)
