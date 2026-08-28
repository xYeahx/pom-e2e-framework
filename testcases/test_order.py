"""用例层 TC-04：订单确认（FR-09）。"""
import pytest

from business.cart_service import CartService
from business.login_service import LoginService
from business.order_service import OrderService
from business.shop_service import ShopService
from common.config_loader import get_data

ACCOUNTS = get_data("accounts.yaml")
PRODUCTS = get_data("products.yaml")


@pytest.mark.smoke
class TestOrder:
    """订单确认与提交用例。"""

    def test_submit_order(self, driver, base_url):
        """TC-04 已进入结算流程：填写信息 -> 确认订单 -> 提交 -> 下单成功。"""
        user = ACCOUNTS["standard_user"]
        LoginService(driver).open_login_page(base_url) \
            .login(user["username"], user["password"])

        shop = ShopService(driver)
        shop.open_inventory(base_url)
        product = PRODUCTS["product"]
        shop.add_to_cart(product)

        cart = CartService(driver)
        cart.open_cart(base_url)
        assert cart.checkout() is True, "应进入结算信息页"

        order = OrderService(driver)
        order.fill_and_continue(user["first_name"], user["last_name"], user["postal_code"])
        assert product in order.get_overview_items(), "订单确认页应展示已购商品"
        assert "Thank you" in order.submit_order(), "提交订单后应出现下单成功文案"
