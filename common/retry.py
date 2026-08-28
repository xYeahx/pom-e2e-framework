"""失败重试装饰器：处理偶发的元素定位/点击不稳定问题（FR-14 配套）。"""
import time
from functools import wraps

from common.logger import get_logger

logger = get_logger("retry")


def retry(attempts: int = 3, interval: float = 1.0, exceptions=(Exception,), description: str = ""):
    """重试装饰器：最多尝试 attempts 次，每次间隔 interval 秒。"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for i in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if i < attempts:
                        logger.warning(
                            "%s 第 %s/%s 次失败: %s，%.1fs 后重试",
                            description or func.__name__, i, attempts, exc, interval,
                        )
                        time.sleep(interval)
            raise last_exc

        return wrapper

    return decorator
