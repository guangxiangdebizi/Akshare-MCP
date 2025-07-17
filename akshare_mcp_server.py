#!/usr/bin/env python3
"""
AkShare MCP 服务器
提供 AkShare 金融数据接口的 MCP 工具集成
"""

import os
import json
import logging
from dataclasses import dataclass
from typing import Optional, Annotated
from datetime import datetime

import akshare as ak
import pandas as pd
from fastmcp import FastMCP
from pydantic import Field

# 导入工具函数
from tools.stock_us_hist import stock_us_hist
from tools.stock_hk_hist import stock_hk_hist
from tools.stock_zh_a_hist import stock_zh_a_hist

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/akshare_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8005"))
    transport: str = os.getenv("TRANSPORT", "sse")
    server_name: str = "AkShare-MCP-Server"

# 创建MCP实例
mcp = FastMCP("AkShare数据服务")

# 注册工具
mcp.tool()(stock_us_hist)
mcp.tool()(stock_hk_hist)
mcp.tool()(stock_zh_a_hist)

def main():
    """启动MCP服务器"""
    config = ServerConfig()
    
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    logger.info(f"启动 {config.server_name}")
    logger.info(f"传输协议: {config.transport}")
    logger.info(f"服务地址: {config.host}:{config.port}")
    
    try:
        # 启动SSE服务器
        mcp.run(
            transport=config.transport,
            host=config.host,
            port=config.port
        )
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise

if __name__ == "__main__":
    main() 