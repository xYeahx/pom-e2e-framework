"""用例层 TC-03：购物车结算（FR-08）。"""
import pytest

from business.cart_service import CartService
from business.login_service import LoginService
from business.shop_service import ShopService
from common.config_loader import get_data

ACCOUNTS = get_data("accounts.yaml")
PRODUCTS = get_data("products.yaml")


@pytest.mark.smoke
class TestCart:
    """购物车结算用例。"""

    def test_cart_checkout(self, driver, base_url):
        """TC-03 购物车有商品：校验条目与数量 -> 点击结算进入订单确认流程。"""
        user = ACCOUNTS["standard_user"]
        LoginService(driver).open_login_page(base_url) \
            .login(user["username"], user["password"])

        shop = ShopService(driver)
        shop.open_inventory(base_url)
        product = PRODUCTS["product"]
        shop.add_to_cart(product)

        cart = CartService(driver)
        cart.open_cart(base_url)
        items = cart.get_cart_items()
        assert product in items, "购物车应包含已加购商品"
        assert cart.get_quantity(product) == "1", "购物车商品数量应为 1"
        assert cart.checkout() is True, "点击结算后应跳转到结算信息页"
