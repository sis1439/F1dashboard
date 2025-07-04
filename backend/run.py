#!/usr/bin/env python3
"""
F1 Dashboard API 启动脚本
"""
import sys
import os
import uvicorn

# 添加 src 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

if __name__ == "__main__":
    # 启动应用
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 