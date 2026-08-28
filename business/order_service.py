"""业务操作层：订单确认与提交业务（FR-09）。"""
from common.logger import get_logger
from pages.checkout_info_page import CheckoutInfoPage
from pages.checkout_overview_page import CheckoutOverviewPage
from pages.order_complete_page import OrderCompletePage

logger = get_logger("order_service")


class OrderService:
    """结算信息填写、订单确认与提交业务动作。"""

    def __init__(self, driver):
        self.driver = driver
        self.checkout_info_page = CheckoutInfoPage(driver)
        self.checkout_overview_page = CheckoutOverviewPage(driver)
        self.order_complete_page = OrderCompletePage(driver)

    def fill_checkout_info(self, first_name: str, last_name: str, postal_code: str):
        """填写结算信息（不点击继续）。"""
        self.checkout_info_page.fill_checkout_info(first_name, last_name, postal_code)
        logger.info("已填写结算信息")
        return self

    def continue_checkout(self) -> bool:
        """点击继续，返回是否成功进入订单确认页。"""
        self.checkout_info_page.click_continue()
        ok = self.checkout_overview_page.is_visible(self.checkout_overview_page.summary_total, timeout=10)
        logger.info("进入订单确认页: %s", "是" if ok else "否")
        return ok

    def fill_and_continue(self, first_name: str, last_name: str, postal_code: str):
        """填写结算信息并进入订单确认页（正向流程）。"""
        self.fill_checkout_info(first_name, last_name, postal_code)
        if not self.continue_checkout():
            raise AssertionError("填写结算信息后未进入订单确认页")
        return self

    def get_checkout_error(self) -> str:
        """返回结算信息必填校验失败提示（无则返回空串）。"""
        return self.checkout_info_page.get_error_message()

    def get_overview_items(self) -> list:
        """返回订单确认页商品列表。"""
        return self.checkout_overview_page.get_item_names()

    def get_total_text(self) -> str:
        """返回订单金额文案。"""
        return self.checkout_overview_page.get_total_text()

    def submit_order(self) -> str:
        """确认订单并提交，返回下单成功页标题文案。"""
        self.checkout_overview_page.click_finish()
        header = self.order_complete_page.get_complete_header()
        logger.info("订单提交成功，成功页文案: %s", header)
        return header
