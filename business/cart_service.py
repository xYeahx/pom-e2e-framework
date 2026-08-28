"""业务操作层：购物车结算业务（FR-08）。"""
from common.logger import get_logger
from pages.cart_page import CartPage
from pages.checkout_info_page import CheckoutInfoPage

logger = get_logger("cart_service")


class CartService:
    """购物车条目校验与结算业务动作。"""

    def __init__(self, driver):
        self.driver = driver
        self.cart_page = CartPage(driver)
        self.checkout_info_page = CheckoutInfoPage(driver)

    def open_cart(self, base_url: str):
        """打开购物车页并等待就绪。"""
        self.driver.get(f"{base_url.rstrip('/')}/cart.html")
        self.cart_page.wait_until_visible(self.cart_page.page_title, timeout=10)
        return self

    def get_cart_items(self) -> list:
        """返回购物车商品名称列表。"""
        return self.cart_page.get_item_names()

    def get_quantity(self, product_name: str) -> str:
        """返回指定商品数量。"""
        return self.cart_page.get_quantity(product_name)

    def checkout(self) -> bool:
        """点击结算，返回是否已进入结算信息页。"""
        self.cart_page.click_checkout()
        ok = self.checkout_info_page.is_visible(self.checkout_info_page.first_name_input, timeout=10)
        logger.info("点击结算，进入结算信息页: %s", "是" if ok else "否")
        return ok
