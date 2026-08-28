"""用例层 TC-02：搜索与筛选加购（FR-06/FR-07）。"""
import pytest

from business.login_service import LoginService
from business.shop_service import ShopService
from common.config_loader import get_data

ACCOUNTS = get_data("accounts.yaml")
PRODUCTS = get_data("products.yaml")


@pytest.mark.smoke
class TestShop:
    """商品筛选与加购用例。"""

    def test_filter_and_add_to_cart(self, driver, base_url):
        """TC-02 已登录：筛选商品 -> 进入详情 -> 加购 -> 购物车数量 +1。"""
        user = ACCOUNTS["standard_user"]
        LoginService(driver).open_login_page(base_url) \
            .login(user["username"], user["password"])

        shop = ShopService(driver)
        shop.open_inventory(base_url)
        prices = shop.filter_products(PRODUCTS["filter_option"])
        assert prices == sorted(prices), "按价格升序筛选后价格应有序"

        product_name = PRODUCTS["product"]
        assert product_name in shop.inventory_page.get_product_names(), "目标商品应出现在列表"
        after_count = shop.add_to_cart(product_name)
        assert after_count >= 1, "加购后购物车数量应 >= 1"
