#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄金价格看板数据服务 - 金十数据版本
使用金十数据 MCP API 获取实时数据

=========================================
使用前请配置你的 API Token！
=========================================

方式一（推荐）：在同级目录创建 .env 文件，内容如下：
    JIN10_TOKEN=你的金十数据API Token

方式二：设置系统环境变量 JIN10_TOKEN

Token 申请地址：https://www.jin10.com/
"""

import json
import os
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 导入金十数据客户端
from jin10_api import Jin10API as Jin10MCPClient

app = FastAPI(title="Gold Dashboard Data Service - Jin10", version="1.0.0")

# 启用CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# API 配置 - 请填写你自己的 Token！
# ============================================================
JIN10_TOKEN = os.environ.get("JIN10_TOKEN", "")

if not JIN10_TOKEN:
    # 尝试从 .env 文件读取
    _env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(_env_file):
        for line in open(_env_file, "r", encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "JIN10_TOKEN":
                    JIN10_TOKEN = v.strip().strip('"')

if not JIN10_TOKEN:
    print("=" * 60)
    print("  ⚠️  未检测到金十数据 API Token！")
    print("")
    print("  请在同目录下创建 .env 文件并填入 Token：")
    print("    echo JIN10_TOKEN=你的Token > .env")
    print("")
    print("  或设置环境变量：")
    print("    set JIN10_TOKEN=你的Token")
    print("")
    print("  Token 申请地址：https://www.jin10.com/")
    print("=" * 60)

# 初始化客户端
jin10_client = None


@app.on_event("startup")
async def startup_event():
    """启动时初始化金十客户端"""
    global jin10_client
    try:
        jin10_client = Jin10MCPClient(token=JIN10_TOKEN)
        # 必须调用 initialize 建立 MCP Session
        if jin10_client.initialize():
            print("Jin10 MCP client initialized successfully")
        else:
            print("Jin10 MCP initialize failed!")
            jin10_client = None
    except Exception as e:
        print(f"Jin10 init error: {e}")
        jin10_client = None


@app.get("/")
async def root():
    return {
        "message": "Gold Dashboard Data Service - Jin10",
        "status": "running",
        "data_source": "Jin10 Financial Data"
    }


@app.get("/api/jin10/gold")
async def get_jin10_gold():
    """获取金十黄金数据"""
    if not jin10_client:
        raise HTTPException(status_code=503, detail="Jin10 client not available")

    try:
        quote = jin10_client.call_tool("get_quote", {"code": "XAUUSD"})
        return JSONResponse(content=quote)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jin10/oil")
async def get_jin10_oil():
    """获取金十原油数据"""
    if not jin10_client:
        raise HTTPException(status_code=503, detail="Jin10 client not available")

    try:
        quote = jin10_client.call_tool("get_quote", {"code": "USOIL"})
        return JSONResponse(content=quote)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jin10/usdjpy")
async def get_jin10_usdjpy():
    """获取金十美元/日元数据"""
    if not jin10_client:
        raise HTTPException(status_code=503, detail="Jin10 client not available")

    try:
        quote = jin10_client.call_tool("get_quote", {"code": "USDJPY"})
        return JSONResponse(content=quote)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jin10/flash-news")
async def get_jin10_flash(keyword: str = "黄金"):
    """获取金十快讯"""
    if not jin10_client:
        raise HTTPException(status_code=503, detail="Jin10 client not available")

    try:
        news = jin10_client.call_tool("search_flash", {"keyword": keyword})
        return JSONResponse(content=news)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jin10/calendar")
async def get_jin10_calendar():
    """获取金十财经日历"""
    if not jin10_client:
        raise HTTPException(status_code=503, detail="Jin10 client not available")

    try:
        calendar = jin10_client.call_tool("list_calendar", {})
        return JSONResponse(content=calendar)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard")
async def get_dashboard_data():
    """获取完整看板数据（金十数据）"""
    if not jin10_client:
        raise HTTPException(status_code=503, detail="Jin10 client not available")

    try:
        # 使用 Jin10API 已封装好的方法（自动处理MCP协议解析）
        gold_quote = jin10_client.get_quote("XAUUSD") or {}
        eurusd_quote = jin10_client.get_quote("EURUSD") or {}  # 金十支持 EURUSD
        usdjpy_quote = jin10_client.get_quote("USDJPY") or {}
        news_data = jin10_client.search_flash("黄金") or {}

        # 提取黄金数据
        gold_price = float(gold_quote.get("close", 0))
        gold_change = float(gold_quote.get("ups_percent", 0))

        # 简单的信号判断（基于价格变动）
        if gold_change > 0.5:
            gold_signal = "bullish"
            gold_text = "上涨"
        elif gold_change < -0.5:
            gold_signal = "bearish"
            gold_text = "下跌"
        else:
            gold_signal = "neutral"
            gold_text = "震荡"

        # 构建统一响应
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "data_source": "Jin10 Financial Data",
            "gold": {
                "price": gold_price,
                "change": gold_change,
                "open": gold_quote.get("open", "--"),
                "high": gold_quote.get("high", "--"),
                "low": gold_quote.get("low", "--"),
                "time": gold_quote.get("time", "--"),
                "signal": gold_signal,
                "text": gold_text
            },
            "eurusd": {
                "price": float(eurusd_quote.get("close", 0)),
                "change": float(eurusd_quote.get("ups_percent", 0)),
                "name": eurusd_quote.get("name", "欧元/美元"),
                "note": "与DXY高度负相关",
                "open": eurusd_quote.get("open", "--"),
                "high": eurusd_quote.get("high", "--"),
                "low": eurusd_quote.get("low", "--"),
            },
            "usdjpy": {
                "price": float(usdjpy_quote.get("close", 0)),
                "change": float(usdjpy_quote.get("ups_percent", 0)),
                "name": usdjpy_quote.get("name", "美元/日元"),
                "open": usdjpy_quote.get("open", "--"),
                "high": usdjpy_quote.get("high", "--"),
                "low": usdjpy_quote.get("low", "--"),
            },
            "news": news_data.get("items", [])[:5] if isinstance(news_data, dict) else [],
            "signals": {
                "gold": {
                    "value": gold_price,
                    "signal": gold_signal,
                    "text": gold_text
                },
                "overall": {
                    "score": max(0, min(100, 50 + (gold_change * 10))),
                    "signal": gold_signal,
                    "action": get_action_text(gold_change),
                    "signal_text": "看多" if gold_signal == "bullish" else ("看空" if gold_signal == "bearish" else "观望")
                }
            }
        }

        return JSONResponse(content=dashboard_data)
    except Exception as e:
        import traceback
        print(f"Dashboard error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def get_action_text(change: float) -> str:
    """根据价格变动获取操作建议"""
    if change > 1:
        return "强势上涨 - 考虑获利了结"
    elif change > 0.5:
        return "上涨动能 - 持有多单"
    elif change < -1:
        return "大幅下跌 - 考虑止损"
    elif change < -0.5:
        return "下跌趋势 - 关注支撑位"
    else:
        return "震荡整理 - 等待突破"


if __name__ == "__main__":
    print("=" * 70)
    print("     黄金价格看板数据服务 - 金十数据版")
    print("=" * 70)
    print("\n数据来源：金十数据 MCP API")
    print("\nAPI 接口：")
    print("  - http://localhost:8002/api/dashboard")
    print("  - http://localhost:8002/api/jin10/gold")
    print("  - http://localhost:8002/api/jin10/oil")
    print("  - http://localhost:8002/api/jin10/flash-news")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8002)
