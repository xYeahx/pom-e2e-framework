# Web UI 自动化测试框架（Python + Selenium + pytest + PO 分层）

基于 **Python + Selenium + pytest** 的电商 Web UI 自动化测试框架，采用 **PO 分层架构**（页面层 → 业务操作层 → 用例层），覆盖电商核心链路冒烟：**登录 → 商品筛选 → 加购 → 购物车结算 → 订单确认**，并配套 **GitHub Actions CI 流水线**与**负向用例**（登录失败、非法输入）。

> 目标站点：本项目使用公开稳定的演示电商站点 [SauceDemo](https://www.saucedemo.com)，支持全链路场景且元素稳定，适合框架实战。可在 `config/config.yaml` 中替换为目标站点（仅需同步修改页面层定位信息）。

---

## 1. 环境准备

- Python 3.10+
- 已安装 Chrome / Edge / Firefox 浏览器（任一即可，默认 Chrome）

## 2. 安装步骤

```bash
pip install -r requirements.txt
```

依赖会自动安装：
| 依赖 | 用途 |
| --- | --- |
| selenium | Web UI 自动化 |
| webdriver-manager | 自动下载/匹配浏览器驱动（不可用时自动回退 Selenium Manager） |
| pytest | 用例组织与断言 |
| pytest-html | HTML 测试报告 |
| PyYAML | 配置与测试数据读取 |

## 3. 运行命令

```bash
# 运行全部用例（含负向用例）
python -m pytest

# 一键运行冒烟套件（TC-01 ~ TC-05）
python -m pytest -m smoke

# 运行负向用例（登录失败、非法输入等，不纳入冒烟套件）
python -m pytest -m negative

# 无头模式运行（CI 推荐），支持环境变量 HEADLESS=1
$env:HEADLESS = "1"; python -m pytest -m smoke
```

Windows 下也可直接双击/运行脚本：

```powershell
.\run_smoke.ps1    # 冒烟套件（生成 reports/smoke_report.html）
.\run_all.ps1      # 全部用例（含负向）
```

运行后产出：

- `reports/report.html`：HTML 测试报告（含通过率、失败原因与截图）
- `reports/smoke_report.html` / `reports/negative_report.html`：冒烟/负向套件独立报告（CI 中生成）
- `logs/run.log`：分级运行日志（INFO 操作步骤 / ERROR 失败堆栈）
- `screenshots/`：用例失败自动截图（命名：用例名_时间戳.png）

## 4. 目录说明

```
pom-e2e-framework/
├── .github/workflows/  # GitHub Actions CI 流水线
│   └── ci.yml              # push/PR/手动触发：安装 Chrome → 冒烟 → 负向 → 上传报告与截图
├── config/            # 全局配置：浏览器、headless、超时、URL、弹窗配置
├── common/            # 公共能力层
│   ├── config_loader.py   # YAML 配置/数据加载（带缓存）
│   ├── logger.py          # 分级日志（控制台 + 文件，滚动写入）
│   ├── driver_manager.py  # WebDriver 工厂（Chrome/Edge/Firefox）
│   ├── base_page.py       # BasePage：显性等待/点击输入/多级定位/弹窗/截图
│   └── retry.py           # 失败重试装饰器
├── pages/             # 页面层（Page）：元素定位 + 页面操作，前端改版只改这里
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── product_detail_page.py
│   ├── cart_page.py
│   ├── checkout_info_page.py
│   ├── checkout_overview_page.py
│   └── order_complete_page.py
├── business/          # 业务操作层（Service）：组合页面操作形成业务动作
│   ├── login_service.py
│   ├── shop_service.py
│   ├── cart_service.py
│   └── order_service.py
├── testcases/         # 用例层：只调用业务层 + 断言
│   ├── test_login.py            # TC-01 登录成功（smoke）
│   ├── test_shop.py             # TC-02 筛选与加购（smoke）
│   ├── test_cart.py             # TC-03 购物车结算（smoke）
│   ├── test_order.py            # TC-04 订单确认（smoke）
│   ├── test_smoke_flow.py       # TC-05 全链路冒烟（smoke）
│   ├── test_login_negative.py   # 登录负向：密码错误/锁定账号/空账号/空密码（negative）
│   └── test_checkout_negative.py# 结算负向：姓/名/邮编必填校验（negative）
├── data/              # 测试数据（账号、商品数据），与脚本分离
├── conftest.py        # pytest fixture（Driver 生命周期、失败截图钩子）
├── pytest.ini         # pytest 配置（markers、报告、testpaths）
├── requirements.txt
└── run_smoke.ps1 / run_all.ps1
```

## 5. 分层架构

依赖方向单向：**用例层 → 业务操作层 → 页面层**

| 层次 | 职责 | 改版影响 |
| --- | --- | --- |
| 页面层 Page | 元素定位 + 页面操作，元素集中维护 | 前端改版仅改此层 |
| 业务操作层 Service | 组合页面操作形成可复用业务动作（登录、筛选加购、结算、下单） | 业务变更仅改此层 |
| 用例层 TestCase | 场景描述 + 断言，不接触任何元素定位 | 用例即业务场景，可读性高 |

## 6. 稳定性保障（对应需求 FR-11 ~ FR-16）

| 能力 | 实现位置 | 说明 |
| --- | --- | --- |
| 显性等待 | `common/base_page.py` | 可见/可点击/存在/消失/文本出现，超时与轮询间隔可配置 |
| 异步加载 | `wait_loading_done()` | 等待 loading 指示器消失 |
| 弹窗遮挡 | `handle_popups()` + `config.yaml` 的 `popups` 配置 | 自动关闭 Cookie/广告弹窗；点击被遮挡时降级 JS 点击 |
| 多级定位 | 定位器支持 `[(主), (备选)]` 列表 | 主定位失效自动尝试备选（见 `LoginPage.login_button` 示例） |
| 详情页跳转兜底 | `pages/inventory_page.py` 的 `open_product_detail()` | 商品跳转由站点 JS 路由处理，普通点击未触发跳转时自动降级 JS 点击（适配 SauceDemo 新版前端） |
| 失败截图 | `conftest.py` 钩子 | 失败自动截图并附加到 HTML 报告 |
| 运行日志 | `common/logger.py` | INFO/ERROR 分级，记录操作步骤、定位信息、失败堆栈 |

## 7. CI 持续集成（GitHub Actions）

流水线文件：`.github/workflows/ci.yml`，触发方式：

- `push` 到 `main` / `master` 分支
- 任意 `pull_request`
- 手动触发：仓库 Actions 页面 → Run workflow（`workflow_dispatch`）

执行步骤：

1. Checkout 代码
2. Setup Python 3.10（pip 缓存）
3. 安装 Chrome（稳定版）
4. 安装依赖 `pip install -r requirements.txt`
5. 无头模式运行冒烟套件（`HEADLESS=1`，`-m smoke`，生成 `reports/smoke_report.html`）
6. 无头模式运行负向套件（`-m negative`，生成 `reports/negative_report.html`）
7. 上传 `reports/`、`screenshots/`、`logs/` 为 CI 产物（失败也可下载，`if: always()`）

本地等效验证命令：

```powershell
$env:HEADLESS = "1"
python -m pytest -m smoke -o addopts="-q --tb=short" --html=reports/smoke_report.html --self-contained-html
python -m pytest -m negative -o addopts="-q --tb=short" --html=reports/negative_report.html --self-contained-html
```

## 8. 可维护性验证（验收标准 4）

模拟前端改版（例如登录按钮 `id` 变更），只需修改 `pages/login_page.py` 中对应定位信息（元素名 + 定位方式 + 表达式），业务层与用例层**零改动**即可重新通过。

## 9. 扩展说明

- **新增页面**：在 `pages/` 新增 Page 类，在 `business/` 新增对应 Service，在 `testcases/` 新增用例即可，无需修改既有用例。
- **新增负向用例**：在 `testcases/` 新增用例并加 `@pytest.mark.negative`，即可纳入负向套件且不影响冒烟。
- **切换目标站点**：修改 `config/config.yaml` 的 `url.base`，同步维护各 Page 定位信息。
- **Allure 报告（可选）**：安装 `allure-pytest` 后，运行 `pytest --alluredir=reports/allure-results`，再执行 `allure serve reports/allure-results`。
- **账号/数据管理**：测试账号在 `data/accounts.yaml`，商品数据在 `data/products.yaml`，支持 pytest 参数化扩展。
- **已知适配说明**：SauceDemo 不支持商品数量修改与规格选择，购物车"修改数量"环节以移除/重新加购替代，相关说明见 `pages/cart_page.py` 注释与用例 TC-03。

## 10. 里程碑对照

| 需求文档阶段 | 本项目产出 |
| --- | --- |
| M1 框架搭建 | config/common/conftest/pytest.ini/requirements 已完成 |
| M2 页面层与业务操作层 | pages/ + business/ 已完成 |
| M3 用例层 | testcases/ TC-01 ~ TC-05 冒烟套件 + 负向用例（登录 4 条 + 结算 3 条）+ HTML 报告 |
| M4 稳定性调优 | 显性等待/弹窗/多级定位/截图/日志/重试/详情页跳转兜底 |
| M5 验证与交付 | 本机全链路冒烟 5/5、负向 7/7 通过，README 归档 |
| M6 CI 集成 | GitHub Actions：冒烟 + 负向自动执行，报告/截图/日志作为产物上传 |