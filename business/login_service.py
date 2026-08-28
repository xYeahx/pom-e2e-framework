"""业务操作层：登录业务动作（FR-05）。"""
from common.logger import get_logger
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

logger = get_logger("login_service")


class LoginService:
    """登录相关业务动作，供用例层调用，不暴露页面元素。"""

    def __init__(self, driver):
        self.driver = driver
        self.login_page = LoginPage(driver)

    def open_login_page(self, base_url: str):
        """打开登录页。"""
        self.driver.get(base_url)
        self.login_page.wait_until_visible(self.login_page.login_logo, timeout=10)
        return self

    def login(self, username: str, password: str):
        """输入账号密码并提交登录。"""
        self.login_page.input_username(username)
        self.login_page.input_password(password)
        self.login_page.click_login()
        logger.info("执行登录: %s", username)
        return self

    def is_logged_in(self) -> bool:
        """登录成功后应跳转到商品列表页。"""
        return InventoryPage(self.driver).is_visible(InventoryPage.page_title, timeout=10)

    def login_and_verify(self, username: str, password: str) -> bool:
        """完整登录动作 + 登录结果校验。"""
        self.login(username, password)
        ok = self.is_logged_in()
        logger.info("登录校验结果: %s", "成功" if ok else "失败")
        return ok

    def get_login_error(self) -> str:
        """返回登录失败提示文案（无则返回空串），供负向用例断言。"""
        return self.login_page.get_error_message()

    def is_on_login_page(self) -> bool:
        """判断当前是否停留在登录页（登录失败场景）。"""
        return self.login_page.is_visible(self.login_page.login_logo, timeout=10)
