"""业务操作层：商品筛选与加购业务（FR-06/FR-07）。"""
from common.logger import get_logger
from pages.inventory_page import InventoryPage
from pages.product_detail_page import ProductDetailPage

logger = get_logger("shop_service")


class ShopService:
    """筛选商品、进入详情、加购等业务动作。"""

    def __init__(self, driver):
        self.driver = driver
        self.inventory_page = InventoryPage(driver)
        self.detail_page = ProductDetailPage(driver)

    def open_inventory(self, base_url: str):
        """打开商品列表页并等待就绪。"""
        self.driver.get(f"{base_url.rstrip('/')}/inventory.html")
        self.inventory_page.wait_until_visible(self.inventory_page.page_title, timeout=10)
        return self

    def filter_products(self, option_text: str) -> list:
        """应用筛选/排序条件，返回筛选后的商品价格列表供用例断言。"""
        self.inventory_page.sort_products(option_text)
        prices = self.inventory_page.get_product_prices()
        logger.info("筛选条件[%s]生效，商品数=%s", option_text, len(prices))
        return prices

    def add_to_cart(self, product_name: str) -> int:
        """进入商品详情并加购，返回加购后的购物车数量。"""
        self.inventory_page.open_product_detail(product_name)
        self.detail_page.wait_until_visible(self.detail_page.product_name, timeout=self.detail_page.long_timeout)
        before = self.detail_page.get_cart_count()
        self.detail_page.click_add_to_cart()
        self.detail_page.wait_until(
            lambda _: self.detail_page.get_cart_count() == before + 1,
            "等待购物车数量 +1",
            timeout=self.detail_page.long_timeout,
        )
        after = self.detail_page.get_cart_count()
        logger.info("加购 [%s]: 购物车数量 %s -> %s", product_name, before, after)
        return after
