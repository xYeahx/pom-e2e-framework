"""配置加载：集中读取 config/config.yaml 与 data/ 目录下的测试数据。"""
from functools import lru_cache
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=None)
def get_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict:
    """读取全局配置文件（带缓存，FR-17）。"""
    return _load_yaml(Path(config_path))


@lru_cache(maxsize=None)
def get_data(filename: str) -> dict:
    """读取 data/ 目录下的测试数据文件（带缓存，FR-18）。"""
    return _load_yaml(PROJECT_ROOT / "data" / filename)


def project_root() -> Path:
    """返回项目根目录。"""
    return PROJECT_ROOT
