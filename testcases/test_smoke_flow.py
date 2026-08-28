"""用例层 TC-05：全链路冒烟（FR-10）。

登录 -> 筛选加购 -> 购物车结算 -> 订单确认，覆盖电商核心链路。
"""
import pytest

from business.cart_service import CartService
from business.login_service import LoginService
from business.order_service import OrderService
from business.shop_service import ShopService
from common.config_loader import get_data

ACCOUNTS = get_data("accounts.yaml")
PRODUCTS = get_data("products.yaml")


@pytest.mark.smoke
class TestSmokeFlow:
    """全链路冒烟用例。"""

    def test_full_flow(self, driver, base_url):
        """TC-05 全链路：登录 -> 筛选加购 -> 购物车结算 -> 订单确认。"""
        user = ACCOUNTS["standard_user"]

        # 步骤 1：登录
        login = LoginService(driver)
        login.open_login_page(base_url)
        assert login.login_and_verify(user["username"], user["password"]), "登录应成功"

        # 步骤 2：筛选商品并加购
        shop = ShopService(driver)
        shop.open_inventory(base_url)
        prices = shop.filter_products(PRODUCTS["filter_option"])
        assert prices == sorted(prices), "按价格升序筛选后价格应有序"
        product = PRODUCTS["product"]
        assert shop.add_to_cart(product) >= 1, "加购后购物车数量应 >= 1"

        # 步骤 3：购物车结算
        cart = CartService(driver)
        cart.open_cart(base_url)
        assert product in cart.get_cart_items(), "购物车应包含已加购商品"
        assert cart.checkout() is True, "应进入结算信息页"

        # 步骤 4：订单确认与提交
        order = OrderService(driver)
        order.fill_and_continue(user["first_name"], user["last_name"], user["postal_code"])
        assert product in order.get_overview_items(), "订单确认页应展示已购商品"
        assert "Thank you" in order.submit_order(), "提交订单后应出现下单成功文案"
