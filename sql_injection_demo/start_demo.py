#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL注入演示系统启动脚本
SQL Injection Demo System Startup Script

这个脚本用于在Windows环境下正确启动演示系统
This script is used to properly start the demo system on Windows
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import flask
        print("✅ Flask 已安装 | Flask installed")
        return True
    except ImportError:
        print("❌ Flask 未安装，正在安装... | Flask not installed, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
            print("✅ Flask 安装完成 | Flask installation completed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Flask 安装失败 | Flask installation failed")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔐 SQL注入攻击与防御演示系统")
    print("   SQL Injection Demo System")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出... | Press Enter to exit...")
        return
    
    # 检查主文件是否存在
    demo_file = Path("flask_sql_injection_demo.py")
    if not demo_file.exists():
        print("❌ 演示文件不存在 | Demo file not found")
        input("按回车键退出... | Press Enter to exit...")
        return
    
    print("\n🚀 启动演示系统... | Starting demo system...")
    print("📍 访问地址 | Access URL: http://127.0.0.1:5000")
    print("⚠️  请在浏览器中打开上述地址 | Please open the above URL in browser")
    print("🛑 按 Ctrl+C 停止服务 | Press Ctrl+C to stop service")
    print("=" * 60)
    
    try:
        # 启动Flask应用
        os.system("python flask_sql_injection_demo.py")
    except KeyboardInterrupt:
        print("\n\n🛑 服务已停止 | Service stopped")
    except Exception as e:
        print(f"\n❌ 启动失败 | Startup failed: {e}")
    
    input("\n按回车键退出... | Press Enter to exit...")

if __name__ == "__main__":
    main() 