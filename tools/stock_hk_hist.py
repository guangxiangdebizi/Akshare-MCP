import json
import logging
from typing import Annotated
from datetime import datetime
import akshare as ak
import pandas as pd
from pydantic import Field

logger = logging.getLogger(__name__)

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
        if period not in ['daily', 'weekly', 'monthly']:
            return json.dumps({
                "error": "period参数必须是 'daily', 'weekly', 'monthly' 之一",
                "code": "INVALID_PERIOD"
            }, ensure_ascii=False)
        try:
            datetime.strptime(start_date, "%Y%m%d")
            datetime.strptime(end_date, "%Y%m%d")
        except ValueError:
            return json.dumps({
                "error": "日期格式错误，请使用 YYYYMMDD 格式",
                "code": "INVALID_DATE_FORMAT"
            }, ensure_ascii=False)
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
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        md_table = df.to_markdown(index=False, floatfmt='.2f')
        result = f"""# 港股历史行情数据
\n**股票代码**: {symbol}  \n**数据周期**: {period}  \n**日期范围**: {start_date} ~ {end_date}  \n**复权方式**: {'不复权' if adjust == '' else '前复权' if adjust == 'qfq' else '后复权'}  \n**数据条数**: {len(df)} 条  \n**货币单位**: 港元 (HKD)
\n{md_table}
\n*数据来源：东方财富网*\n"""
        logger.info(f"成功获取港股数据，共 {len(df)} 条记录")
        return result
    except Exception as e:
        error_msg = f"获取港股历史数据失败: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "error": error_msg,
            "code": "API_ERROR"
        }, ensure_ascii=False) 