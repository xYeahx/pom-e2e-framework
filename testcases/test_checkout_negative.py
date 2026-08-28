"""用例层：结算信息非法输入负向用例（FR-09 扩展）。

按需求文档约定，负向用例作为扩展补充，不纳入冒烟套件（使用 negative 标记）。
"""
import pytest

from business.cart_service import CartService
from business.login_service import LoginService
from business.order_service import OrderService
from business.shop_service import ShopService
from common.config_loader import get_data

ACCOUNTS = get_data("accounts.yaml")
PRODUCTS = get_data("products.yaml")


@pytest.mark.negative
class TestCheckoutNegative:
    """结算信息必填校验场景。"""

    def _prepare_checkout(self, driver, base_url) -> OrderService:
        """前置：登录 -> 加购 -> 进入结算信息页。"""
        user = ACCOUNTS["standard_user"]
        LoginService(driver).open_login_page(base_url).login(user["username"], user["password"])
        shop = ShopService(driver)
        shop.open_inventory(base_url)
        shop.add_to_cart(PRODUCTS["product"])
        cart = CartService(driver)
        cart.open_cart(base_url)
        assert cart.checkout() is True, "应进入结算信息页"
        return OrderService(driver)

    def test_checkout_missing_first_name(self, driver, base_url):
        """姓名为空：应提示 First Name 必填且停留在填写页。"""
        order = self._prepare_checkout(driver, base_url)
        order.fill_checkout_info("", "User", "200000")
        assert not order.continue_checkout(), "缺少必填项时不应进入订单确认页"
        assert "First Name is required" in order.get_checkout_error(), \
            "应提示 First Name 必填"

    def test_checkout_missing_last_name(self, driver, base_url):
        """姓为空：应提示 Last Name 必填。"""
        order = self._prepare_checkout(driver, base_url)
        order.fill_checkout_info("Test", "", "200000")
        assert not order.continue_checkout(), "缺少必填项时不应进入订单确认页"
        assert "Last Name is required" in order.get_checkout_error(), \
            "应提示 Last Name 必填"

    def test_checkout_missing_postal_code(self, driver, base_url):
        """邮编为空：应提示 Postal Code 必填。"""
        order = self._prepare_checkout(driver, base_url)
        order.fill_checkout_info("Test", "User", "")
        assert not order.continue_checkout(), "缺少必填项时不应进入订单确认页"
        assert "Postal Code is required" in order.get_checkout_error(), \
            "应提示 Postal Code 必填"
