# 🥇 Gold Dashboard - 黄金价格智能分析看板

> 基于 **金十数据** 实时行情的黄金价格监控面板，支持黄金/欧元/日元三品种联动，5秒自动刷新。

![数据源](https://img.shields.io/badge/数据源-金十数据-orange)
 ![Python](https://img.shields.io/badge/Python-3.8+-blue)
 ![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 功能亮点

- 📊 **三品种实时行情**：现货黄金(XAUUSD) / 欧元兑美元(EUR/USD) / 美元兑日元(USD/JPY)
- 🔄 **5秒自动刷新**：纯金十数据源，无外部API额度限制
- 💰 **完整OHLC数据**：开盘价、最高价、最低价、实时价格、涨跌幅
- 📰 **黄金快讯**：实时推送黄金相关市场快讯
- ⚡ **价格闪烁动效**：价格变动时的视觉反馈
- 🎨 **毛玻璃UI**：深色主题 + Tailwind CSS 响应式设计

## 📸 预览

| 黄金 | 欧元/美元 | 美元/日元 |
|:---:|:---:|:---:|
| 金色卡片 + 涨跌信号 | 紫色主题 + DXY参考 | 蓝色主题 + 精度适配 |

## 🚀 快速开始

### 1️⃣ 配置 API Token（必须）

在项目根目录创建 `.env` 文件，填入你的金十数据 API Token：

```bash
copy .env.example .env
```

然后编辑 `.env` 文件：

```ini
# ============================================================
# 金十数据 API Token
# 申请地址：https://www.jin10.com/
# ============================================================
JIN10_TOKEN=请输入你自己的金十数据API Token
```

> **没有Token？** 前往 [金十数据官网](https://www.jin10.com/) 注册并申请 API Token。

### 2️⃣ 安装依赖

```bash
pip install fastapi uvicorn requests
```

### 3️⃣ 启动服务

**Windows：**
```bash
start_jin10_server.bat
```

**macOS / Linux：**
```bash
python data_service_jin10.py.example
```
> 注意：上传的是脱敏版本 `data_service_jin10.example.py` 和 `jin10_api.example.py`，使用前需将文件名中的 `.example` 去掉（或修改启动脚本引用路径）。

### 4️⃣ 打开看板

浏览器访问前端页面：
```
index_jin10.html
```

后端 API 默认运行在 `http://localhost:8002`。

## 📁 项目结构

```
gold-dashboard/
├── data_service_jin10.example.py   # 后端 FastAPI 服务（需配置Token）
├── jin10_api.example.py            # 金十MCP客户端封装（需配置Token）
├── index_jin10.html                # 前端单页面看板
├── start_jin10_server.bat          # Windows一键启动脚本
├── PROJECT_SUMMARY.md              # 完整项目文档
└── README.md                       # 本文件
```

## 🔌 API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/dashboard` | 完整看板数据（黄金+欧元+日元+快讯） |
| `GET /api/jin10/gold` | 黄金实时报价 |
| `GET /api/jin10/oil` | 原油实时报价（可选） |
| `GET /api/jin10/usdjpy` | 美元/日元汇率 |
| `GET /api/jin10/flash-news` | 黄金快讯 |
| `GET /api/jin10/calendar` | 财经日历 |

## ⚙️ 配置说明

| 变量 | 必填 | 说明 |
|------|:----:|------|
| `JIN10_TOKEN` | ✅ | 金十数据 API Token，[在此申请](https://www.jin10.com/) |

可选配置（`.env` 文件中取消注释）：

| 变量 | 说明 |
|------|------|
| `TWELVEDATA_APIKEY` | Twelve Data 备用数据源（非必须） |

## 🛠 技术栈

- **后端**：Python + FastAPI + Uvicorn
- **前端**：HTML5 + Tailwind CSS (CDN) + Vanilla JavaScript
- **数据源**：[金十数据 MCP API](https://mcp.jin10.com/mcp)
- **设计**：Glass-morphism 毛玻璃风格 + 响应式布局

## 📋 待办

- [ ] 添加历史K线图表
- [ ] 支持自定义刷新间隔
- [ ] 价格预警通知功能
- [ ] 移动端适配优化

## 📄 License

MIT License — 自由使用、修改和分发。

---

> ⚠️ **免责声明**：本工具仅用于学习和研究目的，不构成任何投资建议。市场有风险，投资需谨慎。
