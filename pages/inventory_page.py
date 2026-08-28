"""页面层：商品列表页（FR-06）。"""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class InventoryPage(BasePage):
    """商品列表页：筛选/排序、查看商品、加购入口、购物车入口。"""

    page_title = (By.CSS_SELECTOR, ".title")
    sort_select = (By.CSS_SELECTOR, "select.product_sort_container")
    cart_link = (By.CSS_SELECTOR, "a.shopping_cart_link")
    cart_badge = (By.CSS_SELECTOR, "span.shopping_cart_badge")
    inventory_items = (By.CSS_SELECTOR, "div.inventory_item")
    item_name = (By.CSS_SELECTOR, "div.inventory_item_name")
    item_price = (By.CSS_SELECTOR, "div.inventory_item_price")

    def sort_products(self, option_text: str):
        """按指定条件排序/筛选商品。"""
        return self.select_option_by_text(self.sort_select, option_text)

    def get_product_names(self) -> list:
        """返回全部商品名称列表。"""
        return [el.text.strip() for el in self.find_elements(self.item_name)]

    def get_product_prices(self) -> list:
        """返回全部商品价格（float）列表。"""
        prices = []
        for el in self.find_elements(self.item_price):
            try:
                prices.append(float(el.text.strip().lstrip("$")))
            except ValueError:
                self.logger.warning("商品价格解析失败: %s", el.text)
        return prices

    def _item_name_locator(self, product_name: str):
        """按商品名定位（XPath 属于页面层定位信息）。"""
        return (By.XPATH, f"//div[contains(@class,'inventory_item_name') and normalize-space(.)='{product_name}']")

    def click_product(self, product_name: str):
        """点击商品名进入详情页。"""
        return self.click(self._item_name_locator(product_name))

    def open_product_detail(self, product_name: str, nav_timeout: float = 12):
        """点击商品名进入详情页，并等待跳转完成。

        当前站点版本的商品跳转由前端 JS 路由处理，普通 Selenium 点击偶发不生效；
        因此先尝试普通点击，若限定时间内 URL 未切换，自动降级为 JS 点击兜底。
        """
        locator = self._item_name_locator(product_name)
        self.click(locator)
        try:
            self.wait_until(
                lambda _: "inventory-item.html" in self.driver.current_url,
                "等待进入商品详情页",
                timeout=nav_timeout,
            )
        except TimeoutException:
            if "inventory-item.html" in self.driver.current_url:
                self.logger.info("普通点击已进入详情页（导航延迟），无需兜底")
            else:
                self.logger.warning("普通点击未触发跳转，降级为 JS 点击: %s", product_name)
                self.click_js(locator)
                self.wait_until(
                    lambda _: "inventory-item.html" in self.driver.current_url,
                    "等待 JS 点击进入商品详情页",
                    timeout=nav_timeout,
                )
        return self

    def item_add_button(self, product_name: str):
        """返回某商品对应的加购按钮定位。"""
        return (
            By.XPATH,
            f"//div[contains(@class,'inventory_item')]"
            f"[.//div[contains(@class,'inventory_item_name') and normalize-space(.)='{product_name}']]"
            f"//button[contains(@id,'add-to-cart')]",
        )

    def click_add_to_cart(self, product_name: str):
        """在列表中直接加购指定商品。"""
        return self.click(self.item_add_button(product_name))

    def get_cart_count(self) -> int:
        """获取购物车角标数量（无角标视为 0）。"""
        if not self.is_present(self.cart_badge, timeout=1):
            return 0
        return int(self.get_text(self.cart_badge))

    def click_cart(self):
        """点击购物车入口。"""
        return self.click(self.cart_link)
