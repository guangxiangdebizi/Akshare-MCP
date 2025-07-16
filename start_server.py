#!/usr/bin/env python3
"""
AkShare MCP 服务器启动脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from akshare_mcp_server import main

if __name__ == "__main__":
    print("正在启动 AkShare MCP 服务器...")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1) 