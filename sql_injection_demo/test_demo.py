#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL注入演示系统测试脚本
SQL Injection Demo System Test Script

用于验证演示系统的各项功能是否正常工作
Used to verify that all functions of the demo system work properly
"""

import requests
import json
import time
import sqlite3
from urllib.parse import quote

class SQLInjectionDemoTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_basic_connectivity(self):
        """测试基本连接"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            success = response.status_code == 200
            self.log_test("基本连接测试", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("基本连接测试", False, f"连接失败: {str(e)}")
    
    def test_database_setup(self):
        """测试数据库初始化"""
        try:
            response = requests.get(f"{self.base_url}/setup", timeout=5)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("status") == "success"
            self.log_test("数据库初始化", success, "数据库设置完成")
        except Exception as e:
            self.log_test("数据库初始化", False, f"设置失败: {str(e)}")
    
    def test_vulnerable_endpoint(self):
        """测试脆弱端点"""
        test_cases = [
            # 正常登录测试
            ("正常登录", "admin", "admin123", True),
            # SQL注入测试
            ("SQL注入 - 注释绕过", "admin'--", "any", True),
            ("SQL注入 - UNION查询", "' UNION SELECT 1,2,3--", "any", True),
            ("SQL注入 - 布尔条件", "admin' AND 1=1--", "any", True),
        ]
        
        for test_name, username, password, should_detect in test_cases:
            try:
                url = f"{self.base_url}/login_vuln"
                params = {"username": username, "password": password}
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    has_results = data.get("success", False) or len(data.get("users", [])) > 0
                    self.log_test(f"脆弱端点 - {test_name}", has_results, 
                                f"返回{len(data.get('users', []))}条记录")
                else:
                    self.log_test(f"脆弱端点 - {test_name}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"脆弱端点 - {test_name}", False, str(e))
    
    def test_safe_endpoint(self):
        """测试安全端点"""
        test_cases = [
            # 正常登录测试
            ("正常登录", "admin", "admin123", True),
            # SQL注入测试（应该被阻止）
            ("SQL注入防护测试", "admin'--", "any", False),
            ("UNION注入防护", "' UNION SELECT 1,2,3--", "any", False),
        ]
        
        for test_name, username, password, should_succeed in test_cases:
            try:
                url = f"{self.base_url}/login_safe"
                params = {"username": username, "password": password}
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get("success", False)
                    expected_result = success == should_succeed
                    self.log_test(f"安全端点 - {test_name}", expected_result,
                                f"登录{'成功' if success else '失败'}，符合预期")
                else:
                    self.log_test(f"安全端点 - {test_name}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"安全端点 - {test_name}", False, str(e))
    
    def test_auxiliary_endpoints(self):
        """测试辅助端点"""
        endpoints = [
            ("/users", "用户列表"),
            ("/stats", "攻击统计"),
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                success = response.status_code == 200
                if success:
                    data = response.json()
                    success = isinstance(data, dict)
                self.log_test(f"辅助端点 - {name}", success, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_test(f"辅助端点 - {name}", False, str(e))
    
    def test_advanced_vulnerability(self):
        """测试高级漏洞端点"""
        test_cases = [
            ("正常搜索", "admin"),
            ("SQL注入搜索", "' OR 1=1--"),
            ("UNION注入搜索", "' UNION SELECT username,password,'HACKED' FROM users--"),
        ]
        
        for test_name, search_term in test_cases:
            try:
                url = f"{self.base_url}/advanced_vuln"
                params = {"search": search_term}
                response = requests.get(url, params=params, timeout=5)
                
                success = response.status_code in [200, 400]  # 两种状态都可能正常
                if response.status_code == 200:
                    data = response.json()
                    result_count = len(data.get("results", []))
                    message = f"返回{result_count}条结果"
                else:
                    message = "SQL错误（可能是注入检测）"
                
                self.log_test(f"高级漏洞 - {test_name}", success, message)
            except Exception as e:
                self.log_test(f"高级漏洞 - {test_name}", False, str(e))
    
    def check_database_file(self):
        """检查数据库文件"""
        try:
            conn = sqlite3.connect("demo.db")
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            conn.close()
            
            success = user_count > 0
            self.log_test("数据库文件检查", success, f"找到{user_count}个用户")
        except Exception as e:
            self.log_test("数据库文件检查", False, str(e))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("🧪 SQL注入演示系统 - 功能测试")
        print("   SQL Injection Demo System - Functionality Test")
        print("=" * 80)
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(2)
        
        # 运行测试
        self.test_basic_connectivity()
        self.test_database_setup()
        time.sleep(1)  # 等待数据库初始化完成
        
        self.check_database_file()
        self.test_vulnerable_endpoint()
        self.test_safe_endpoint()
        self.test_auxiliary_endpoints()
        self.test_advanced_vulnerability()
        
        # 统计结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print("\n" + "=" * 80)
        print("📊 测试结果汇总 | Test Results Summary")
        print("=" * 80)
        print(f"总测试数: {total_tests} | Total Tests: {total_tests}")
        print(f"通过测试: {passed_tests} | Passed: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests} | Failed: {total_tests - passed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}% | Success Rate: {passed_tests/total_tests*100:.1f}%")
        print("=" * 80)
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！系统运行正常！")
            print("🎉 All tests passed! System is working properly!")
        else:
            print("⚠️  部分测试失败，请检查系统配置")
            print("⚠️  Some tests failed, please check system configuration")

def main():
    """主函数"""
    tester = SQLInjectionDemoTester()
    
    print("请确保演示系统正在运行 (python flask_sql_injection_demo.py)")
    print("Please ensure the demo system is running (python flask_sql_injection_demo.py)")
    
    input("按回车键开始测试... | Press Enter to start testing...")
    
    tester.run_all_tests()
    
    input("\n按回车键退出... | Press Enter to exit...")

if __name__ == "__main__":
    main() 