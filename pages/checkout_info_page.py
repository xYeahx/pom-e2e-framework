"""页面层：结算信息填写页（FR-09 前置）。"""
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class CheckoutInfoPage(BasePage):
    """结算信息页：填写收货人姓名与邮编。"""

    first_name_input = (By.ID, "first-name")
    last_name_input = (By.ID, "last-name")
    postal_code_input = (By.ID, "postal-code")
    continue_button = (By.ID, "continue")
    cancel_button = (By.ID, "cancel")
    page_title = (By.CSS_SELECTOR, ".title")
    error_message = (By.CSS_SELECTOR, "h3[data-test='error']")

    def fill_checkout_info(self, first_name: str, last_name: str, postal_code: str):
        """填写结算信息。"""
        self.input_text(self.first_name_input, first_name)
        self.input_text(self.last_name_input, last_name)
        self.input_text(self.postal_code_input, postal_code)

    def click_continue(self):
        """点击继续，进入订单确认页。"""
        return self.click(self.continue_button)

    def get_error_message(self) -> str:
        """获取必填校验失败提示文案（无则返回空串）。"""
        if self.is_visible(self.error_message, timeout=3):
            return self.get_text(self.error_message)
        return ""
