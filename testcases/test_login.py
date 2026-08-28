"""用例层 TC-01：登录成功（FR-05）。"""
import pytest

from business.login_service import LoginService
from common.config_loader import get_data

ACCOUNTS = get_data("accounts.yaml")
STANDARD_USER = ACCOUNTS["standard_user"]


@pytest.mark.smoke
class TestLogin:
    """登录相关用例。"""

    def test_login_success(self, driver, base_url):
        """TC-01 登录成功：输入账号密码提交后进入登录态页面。"""
        service = LoginService(driver)
        service.open_login_page(base_url)
        assert service.login_and_verify(STANDARD_USER["username"], STANDARD_USER["password"]), \
            "登录后应跳转到商品列表页（登录态）"
