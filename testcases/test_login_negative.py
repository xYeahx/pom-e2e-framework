"""用例层：登录负向用例（FR-05 扩展）。

按需求文档约定，负向用例作为扩展补充，不纳入冒烟套件（使用 negative 标记）。
"""
import pytest

from business.login_service import LoginService
from common.config_loader import get_data

ACCOUNTS = get_data("accounts.yaml")
STANDARD_USER = ACCOUNTS["standard_user"]
LOCKED_OUT_USER = ACCOUNTS["locked_out_user"]
INVALID_CREDENTIALS = ACCOUNTS["invalid_credentials"]


@pytest.mark.negative
class TestLoginNegative:
    """登录失败场景。"""

    def test_login_wrong_password(self, driver, base_url):
        """密码错误：应提示账号密码不匹配且停留在登录页。"""
        service = LoginService(driver)
        service.open_login_page(base_url)
        service.login(INVALID_CREDENTIALS["username"], INVALID_CREDENTIALS["password"])
        assert "Username and password do not match" in service.get_login_error(), \
            "密码错误时应提示账号密码不匹配"
        assert service.is_on_login_page(), "登录失败后应停留在登录页"

    def test_login_locked_out_user(self, driver, base_url):
        """锁定账号：应提示账号已被锁定。"""
        service = LoginService(driver)
        service.open_login_page(base_url)
        service.login(LOCKED_OUT_USER["username"], LOCKED_OUT_USER["password"])
        assert "locked out" in service.get_login_error().lower(), \
            "锁定账号登录时应提示已被锁定"
        assert service.is_on_login_page(), "登录失败后应停留在登录页"

    def test_login_empty_fields(self, driver, base_url):
        """账号密码为空：应提示账号必填。"""
        service = LoginService(driver)
        service.open_login_page(base_url)
        service.login("", "")
        assert "Username is required" in service.get_login_error(), \
            "账号为空时应提示必填"

    def test_login_empty_password(self, driver, base_url):
        """密码为空：应提示密码必填。"""
        service = LoginService(driver)
        service.open_login_page(base_url)
        service.login(STANDARD_USER["username"], "")
        assert "Password is required" in service.get_login_error(), \
            "密码为空时应提示必填"
