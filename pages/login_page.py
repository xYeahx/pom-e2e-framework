"""页面层：登录页（FR-05）。

元素定位信息集中维护，前端改版时仅需修改本页定位，业务层与用例层无需改动。
"""
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class LoginPage(BasePage):
    """SauceDemo 登录页。"""

    # 元素定位信息
    username_input = (By.ID, "user-name")
    password_input = (By.ID, "password")
    # 演示多级定位策略（FR-14）：主定位失效时使用备选定位
    login_button = [(By.ID, "login-button"), (By.CSS_SELECTOR, "input[data-test='login-button']")]
    login_logo = (By.CSS_SELECTOR, ".login_logo")
    error_message = (By.CSS_SELECTOR, "h3[data-test='error']")

    def input_username(self, username: str):
        """输入账号。"""
        return self.input_text(self.username_input, username)

    def input_password(self, password: str):
        """输入密码。"""
        return self.input_text(self.password_input, password)

    def click_login(self):
        """点击登录按钮。"""
        return self.click(self.login_button)

    def get_error_message(self) -> str:
        """获取登录失败提示文案（无则返回空串）。"""
        if self.is_visible(self.error_message, timeout=3):
            return self.get_text(self.error_message)
        return ""
