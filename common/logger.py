"""日志模块：分级日志，同时输出到控制台与 logs/ 目录文件（FR-16）。"""
import logging
from logging.handlers import RotatingFileHandler

from common.config_loader import get_config, project_root

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_loggers: dict = {}


def _log_dir():
    cfg = get_config()
    log_dir = project_root() / cfg.get("directories", {}).get("logs", "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_logger(name: str = "framework") -> logging.Logger:
    """获取带文件与控制台输出的 logger（同名复用）。"""
    if name in _loggers:
        return _loggers[name]
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        _log_dir() / "run.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    _loggers[name] = logger
    return logger
