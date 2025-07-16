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

@mcp.tool()
def stock_us_hist(
    symbol: Annotated[str, Field(description="美股代码，例如 '106.TTE' 或 'AAPL'，可通过 ak.stock_us_spot_em() 获取完整代码列表")],
    period: Annotated[str, Field(description="数据周期，可选择 'daily'(日线)、'weekly'(周线)、'monthly'(月线)")] = "daily",
    start_date: Annotated[str, Field(description="开始日期，格式为 YYYYMMDD，例如 '20210101'")] = "20210101", 
    end_date: Annotated[str, Field(description="结束日期，格式为 YYYYMMDD，例如 '20240214'")] = "20240214",
    adjust: Annotated[str, Field(description="复权类型：''(不复权)、'qfq'(前复权)、'hfq'(后复权)")] = ""
) -> str:
    """
    获取美股历史行情数据
    """
    try:
        logger.info(f"获取美股历史数据: symbol={symbol}, period={period}, start_date={start_date}, end_date={end_date}, adjust={adjust}")
        
        # 验证参数
        if period not in ['daily', 'weekly', 'monthly']:
            return json.dumps({
                "error": "period参数必须是 'daily', 'weekly', 'monthly' 之一",
                "code": "INVALID_PERIOD"
            }, ensure_ascii=False)
            
        # 验证日期格式
        try:
            datetime.strptime(start_date, "%Y%m%d")
            datetime.strptime(end_date, "%Y%m%d")
        except ValueError:
            return json.dumps({
                "error": "日期格式错误，请使用 YYYYMMDD 格式",
                "code": "INVALID_DATE_FORMAT"
            }, ensure_ascii=False)
            
        # 调用AkShare接口
        df = ak.stock_us_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        
        if df.empty:
            return json.dumps({
                "error": "未找到数据，请检查股票代码或日期范围",
                "code": "NO_DATA_FOUND"
            }, ensure_ascii=False)
        
        # 转换为Markdown表格格式
        # 格式化日期列显示
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        
        # 生成Markdown表格
        md_table = df.to_markdown(index=False, floatfmt='.2f')
        
        # 添加元信息
        result = f"""# 美股历史行情数据

**股票代码**: {symbol}  
**数据周期**: {period}  
**日期范围**: {start_date} ~ {end_date}  
**复权方式**: {'不复权' if adjust == '' else '前复权' if adjust == 'qfq' else '后复权'}  
**数据条数**: {len(df)} 条  
**货币单位**: 美元 (USD)

{md_table}

*数据来源：东方财富网*
"""
        
        logger.info(f"成功获取数据，共 {len(df)} 条记录")
        return result
        
    except Exception as e:
        error_msg = f"获取美股历史数据失败: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "error": error_msg,
            "code": "API_ERROR"
        }, ensure_ascii=False)

@mcp.tool()
def stock_hk_hist(
    symbol: Annotated[str, Field(description="港股代码，例如 '00593' 或 '08367'，可通过 ak.stock_hk_spot_em() 获取完整代码列表")],
    period: Annotated[str, Field(description="数据周期，可选择 'daily'(日线)、'weekly'(周线)、'monthly'(月线)")] = "daily",
    start_date: Annotated[str, Field(description="开始日期，格式为 YYYYMMDD，例如 '19700101'")] = "19700101", 
    end_date: Annotated[str, Field(description="结束日期，格式为 YYYYMMDD，例如 '22220101'")] = "22220101",
    adjust: Annotated[str, Field(description="复权类型：''(不复权)、'qfq'(前复权)、'hfq'(后复权)")] = ""
) -> str:
    """
    获取港股历史行情数据
    """
    try:
        logger.info(f"获取港股历史数据: symbol={symbol}, period={period}, start_date={start_date}, end_date={end_date}, adjust={adjust}")
        
        # 验证参数
        if period not in ['daily', 'weekly', 'monthly']:
            return json.dumps({
                "error": "period参数必须是 'daily', 'weekly', 'monthly' 之一",
                "code": "INVALID_PERIOD"
            }, ensure_ascii=False)
            
        # 验证日期格式
        try:
            datetime.strptime(start_date, "%Y%m%d")
            datetime.strptime(end_date, "%Y%m%d")
        except ValueError:
            return json.dumps({
                "error": "日期格式错误，请使用 YYYYMMDD 格式",
                "code": "INVALID_DATE_FORMAT"
            }, ensure_ascii=False)
            
        # 调用AkShare接口
        df = ak.stock_hk_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        
        if df.empty:
            return json.dumps({
                "error": "未找到数据，请检查股票代码或日期范围",
                "code": "NO_DATA_FOUND"
            }, ensure_ascii=False)
        
        # 转换为Markdown表格格式
        # 格式化日期列显示
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        
        # 生成Markdown表格
        md_table = df.to_markdown(index=False, floatfmt='.2f')
        
        # 添加元信息
        result = f"""# 港股历史行情数据

**股票代码**: {symbol}  
**数据周期**: {period}  
**日期范围**: {start_date} ~ {end_date}  
**复权方式**: {'不复权' if adjust == '' else '前复权' if adjust == 'qfq' else '后复权'}  
**数据条数**: {len(df)} 条  
**货币单位**: 港元 (HKD)

{md_table}

*数据来源：东方财富网*
"""
        
        logger.info(f"成功获取港股数据，共 {len(df)} 条记录")
        return result
        
    except Exception as e:
        error_msg = f"获取港股历史数据失败: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "error": error_msg,
            "code": "API_ERROR"
        }, ensure_ascii=False)

@mcp.tool()
def stock_zh_a_hist(
    symbol: Annotated[str, Field(description="A股代码，例如 '000001'(平安银行) 或 '603777'，可通过 ak.stock_zh_a_spot_em() 获取完整代码列表")],
    period: Annotated[str, Field(description="数据周期，可选择 'daily'(日线)、'weekly'(周线)、'monthly'(月线)")] = "daily",
    start_date: Annotated[str, Field(description="开始日期，格式为 YYYYMMDD，例如 '20210301'")] = "20210301", 
    end_date: Annotated[str, Field(description="结束日期，格式为 YYYYMMDD，例如 '20240528'")] = "20240528",
    adjust: Annotated[str, Field(description="复权类型：''(不复权)、'qfq'(前复权，保持当前价格不变)、'hfq'(后复权，保证历史价格不变)")] = ""
) -> str:
    """
    获取沪深京A股历史行情数据
    """
    try:
        logger.info(f"获取A股历史数据: symbol={symbol}, period={period}, start_date={start_date}, end_date={end_date}, adjust={adjust}")
        
        # 验证参数
        if period not in ['daily', 'weekly', 'monthly']:
            return json.dumps({
                "error": "period参数必须是 'daily', 'weekly', 'monthly' 之一",
                "code": "INVALID_PERIOD"
            }, ensure_ascii=False)
            
        # 验证日期格式
        try:
            datetime.strptime(start_date, "%Y%m%d")
            datetime.strptime(end_date, "%Y%m%d")
        except ValueError:
            return json.dumps({
                "error": "日期格式错误，请使用 YYYYMMDD 格式",
                "code": "INVALID_DATE_FORMAT"
            }, ensure_ascii=False)
            
        # 调用AkShare接口
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            timeout=None
        )
        
        if df.empty:
            return json.dumps({
                "error": "未找到数据，请检查股票代码或日期范围",
                "code": "NO_DATA_FOUND"
            }, ensure_ascii=False)
        
        # 转换为Markdown表格格式
        # 格式化日期列显示
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        
        # 生成Markdown表格
        md_table = df.to_markdown(index=False, floatfmt='.2f')
        
        # 添加元信息
        result = f"""# A股历史行情数据

**股票代码**: {symbol}  
**数据周期**: {period}  
**日期范围**: {start_date} ~ {end_date}  
**复权方式**: {'不复权' if adjust == '' else '前复权' if adjust == 'qfq' else '后复权'}  
**数据条数**: {len(df)} 条  
**货币单位**: 人民币 (CNY)  
**成交量单位**: 手 (1手=100股)

{md_table}

*数据来源：东方财富网*  
*注：成交量单位为手，成交额单位为元*
"""
        
        logger.info(f"成功获取A股数据，共 {len(df)} 条记录")
        return result
        
    except Exception as e:
        error_msg = f"获取A股历史数据失败: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "error": error_msg,
            "code": "API_ERROR"
        }, ensure_ascii=False)

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