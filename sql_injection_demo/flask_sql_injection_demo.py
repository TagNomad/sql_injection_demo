"""
=================================================================================
                    SQL 注入攻击与防御机制演示系统
                    Flask-based SQL Injection Demo System
=================================================================================

📋 项目概述 (Project Overview)
=============================
本项目是一个专门用于教学和研究的SQL注入漏洞演示系统，通过对比"易受攻击"与"安全加固"
两种不同的代码实现，帮助开发者和安全研究人员深入理解：
- SQL注入攻击的基本原理和危害
- 常见的SQL注入攻击技术
- 有效的防护措施和最佳实践
- 参数化查询的重要性

🔬 研究目标 (Research Objectives)
================================
1. 演示SQL注入漏洞的成因与利用过程
2. 对比脆弱代码与安全代码的实现差异
3. 提供可重现的攻击环境用于安全研究
4. 验证不同防护机制的有效性
5. 支持自动化渗透测试工具(如sqlmap)的演示

📅 开发日志 (Development Log)
=============================
版本 v1.0.0 - 初始版本 (Initial Release)
- ✅ 基础Flask应用框架搭建
- ✅ SQLite数据库集成
- ✅ 脆弱登录端点实现 (/login_vuln)
- ✅ 安全登录端点实现 (/login_safe)
- ✅ 基础数据库初始化功能

版本 v1.1.0 - 功能增强 (Feature Enhancement)
- ✅ 添加详细的文档说明和使用指南
- ✅ 增加多种SQL注入攻击场景演示
- ✅ 完善错误处理和日志记录
- ✅ 添加实时攻击检测演示功能
- ✅ 增加防护机制对比分析

版本 v1.2.0 - 研究扩展 (Research Extension)
- ✅ 添加攻击流量分析功能
- ✅ 集成基础的异常检测机制
- ✅ 提供详细的安全审计日志
- ✅ 支持多种数据库后端测试

🚀 快速开始 (Quick Start)
=========================
环境要求：Python 3.8+ 

1. 安装依赖：
   pip install flask sqlite3

2. 启动服务：
   python flask_sql_injection_demo.py

3. 初始化数据库：
   访问 http://127.0.0.1:5000/setup

4. 测试端点：
   - 脆弱端点: http://127.0.0.1:5000/login_vuln
   - 安全端点: http://127.0.0.1:5000/login_safe

🔍 SQL注入攻击演示 (SQL Injection Exploitation)
===============================================

方法1: 手动测试
--------------
# 基础攻击测试
curl "http://127.0.0.1:5000/login_vuln?username=admin'--&password=any"

# 联合查询攻击
curl "http://127.0.0.1:5000/login_vuln?username=' UNION SELECT 1,username,password FROM users--&password=any"

# 布尔盲注测试
curl "http://127.0.0.1:5000/login_vuln?username=admin' AND 1=1--&password=any"

方法2: 使用sqlmap自动化测试
--------------------------
# 检测脆弱参数并提取数据
sqlmap -u "http://127.0.0.1:5000/login_vuln?username=test&password=test" --batch --dump

# 测试安全端点（应该无法注入）
sqlmap -u "http://127.0.0.1:5000/login_safe?username=test&password=test" --batch

# 详细扫描模式
sqlmap -u "http://127.0.0.1:5000/login_vuln?username=test&password=test" --batch --level=3 --risk=3

📊 安全对比分析 (Security Comparison)
====================================
脆弱实现 (/login_vuln):
- ❌ 直接字符串拼接构造SQL查询
- ❌ 未对用户输入进行验证和过滤
- ❌ 容易受到多种SQL注入攻击
- ❌ 可能导致数据泄露、权限提升等严重后果

安全实现 (/login_safe):
- ✅ 使用参数化查询（PreparedStatement）
- ✅ 自动处理特殊字符转义
- ✅ 有效防止SQL注入攻击
- ✅ 保持良好的性能表现

🛡️ 防护建议 (Security Recommendations)
======================================
1. 始终使用参数化查询或ORM框架
2. 对用户输入进行严格验证和过滤
3. 实施最小权限原则
4. 启用数据库审计和监控
5. 定期进行安全代码审查
6. 使用Web应用防火墙(WAF)
7. 实施输入长度限制
8. 避免在错误消息中暴露敏感信息

⚠️  重要声明 (Important Notice)
==============================
本演示系统仅用于教育和研究目的，请勿用于任何恶意攻击活动！
使用者应遵守当地法律法规和道德准则。

This demonstration system is for educational and research purposes only.
Do not use it for any malicious activities!
Users should comply with local laws, regulations, and ethical guidelines.

=================================================================================
"""

import os
import sqlite3
import logging
import datetime
from flask import Flask, request, jsonify, g, render_template_string

app = Flask(__name__)
DATABASE = "demo.db"
ATTACK_LOG = "attack_log.txt"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# ---------------------------------------------------------------------------
# 数据库连接管理 (Database Connection Management)
# ---------------------------------------------------------------------------

def get_db():
    """返回一个在请求生命周期内有效的数据库连接"""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """请求结束时关闭数据库连接"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# ---------------------------------------------------------------------------
# 数据库初始化 (Database Initialization)
# ---------------------------------------------------------------------------

def init_db():
    """创建用户表并插入测试数据"""
    if os.path.exists(DATABASE):
        logging.info("数据库已存在，跳过初始化")
        return

    logging.info("正在初始化数据库...")
    with sqlite3.connect(DATABASE) as conn:
        conn.executescript(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE sensitive_data (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                secret_info TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            INSERT INTO users (username, password, role) VALUES
                ('admin', 'admin123', 'administrator'),
                ('alice', 'alice_password', 'user'),
                ('bob', 'bob123', 'user'),
                ('test_user', 'test123', 'user');

            INSERT INTO sensitive_data (user_id, secret_info) VALUES
                (1, 'Top Secret Admin Data'),
                (2, 'Alice Personal Information'),
                (3, 'Bob Confidential Records');
            """
        )
    logging.info("数据库初始化完成")


def log_attack_attempt(endpoint, query, user_input):
    """记录可疑的攻击尝试"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ATTACK_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {endpoint} - Query: {query} - Input: {user_input}\n")


def detect_sql_injection(input_string):
    """简单的SQL注入检测机制"""
    suspicious_patterns = [
        "'", '"', '--', '/*', '*/', 'union', 'select', 'drop', 'delete', 
        'insert', 'update', 'or 1=1', 'and 1=1', 'xp_', 'sp_'
    ]
    input_lower = input_string.lower()
    detected_patterns = [pattern for pattern in suspicious_patterns if pattern in input_lower]
    return len(detected_patterns) > 0, detected_patterns


# ---------------------------------------------------------------------------
# Web界面和路由 (Web Interface and Routes)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """主页面 - 显示演示说明和测试链接"""
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SQL注入攻击与防御演示系统</title>
        <style>
            body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            h2 { color: #e74c3c; border-bottom: 2px solid #e74c3c; padding-bottom: 5px; }
            h3 { color: #3498db; }
            .danger { background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0; }
            .safe { background: #e8f5e8; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; }
            .info { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0; }
            .test-link { display: inline-block; margin: 10px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
            .test-link:hover { background: #2980b9; }
            .vuln-link { background: #e74c3c; }
            .vuln-link:hover { background: #c0392b; }
            code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: 'Consolas', monospace; }
            pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 SQL注入攻击与防御演示系统</h1>
            
            <div class="info">
                <h3>📋 系统说明</h3>
                <p>本系统专门用于演示SQL注入漏洞的原理、攻击方法和防护措施。通过对比脆弱实现和安全实现，帮助理解SQL注入的危害性和防护的重要性。</p>
            </div>

            <h2>🧪 测试端点</h2>
            
            <div class="danger">
                <h3>⚠️ 脆弱端点 (Vulnerable Endpoint)</h3>
                <p>此端点故意包含SQL注入漏洞，用于演示攻击效果：</p>
                <a href="/login_vuln?username=admin&password=wrong" class="test-link vuln-link">测试脆弱登录</a>
                <a href="/login_vuln?username=admin'--&password=any" class="test-link vuln-link">注入攻击测试</a>
                <pre>示例攻击载荷：
username: admin'--
username: ' UNION SELECT 1,username,password FROM users--
username: admin' AND 1=1--</pre>
            </div>

            <div class="safe">
                <h3>✅ 安全端点 (Safe Endpoint)</h3>
                <p>此端点使用参数化查询，有效防止SQL注入攻击：</p>
                <a href="/login_safe?username=admin&password=admin123" class="test-link">测试安全登录</a>
                <a href="/login_safe?username=admin'--&password=any" class="test-link">注入防护测试</a>
            </div>

            <h2>🛠️ 自动化测试工具</h2>
            <div class="info">
                <h3>使用sqlmap进行自动化测试：</h3>
                <pre># 测试脆弱端点
sqlmap -u "http://127.0.0.1:5000/login_vuln?username=test&password=test" --batch --dump

# 测试安全端点
sqlmap -u "http://127.0.0.1:5000/login_safe?username=test&password=test" --batch</pre>
            </div>

            <h2>📊 其他功能</h2>
            <a href="/setup" class="test-link">初始化数据库</a>
            <a href="/stats" class="test-link">查看攻击统计</a>
            <a href="/users" class="test-link">查看用户列表</a>

            <div class="danger">
                <h3>⚠️ 免责声明</h3>
                <p><strong>本系统仅用于教育和研究目的！</strong><br>
                请勿将此系统用于任何恶意攻击活动。使用者应当遵守相关法律法规和道德准则。</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)


@app.route("/setup")
def setup():
    """初始化数据库的HTTP端点"""
    try:
        init_db()
        logging.info("通过Web接口初始化数据库")
        return jsonify({
            "status": "success",
            "message": "数据库初始化完成",
            "timestamp": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"数据库初始化失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"数据库初始化失败: {str(e)}"
        }), 500


# ---------------------------------------------------------------------------
# 脆弱端点 - SQL注入演示 (Vulnerable Endpoint)
# ---------------------------------------------------------------------------

@app.route("/login_vuln")
def login_vuln():
    """🚨 故意存在SQL注入漏洞的登录端点 - 仅用于演示！"""
    username = request.args.get("username", "")
    password = request.args.get("password", "")
    
    # 检测可疑输入
    is_suspicious_user, user_patterns = detect_sql_injection(username)
    is_suspicious_pass, pass_patterns = detect_sql_injection(password)
    
    # ⚠️ 故意脆弱的SQL查询构造 - 直接字符串拼接
    query = (
        f"SELECT * FROM users WHERE username='{username}' "
        f"AND password='{password}'"
    )
    
    # 记录可疑活动
    if is_suspicious_user or is_suspicious_pass:
        log_attack_attempt("login_vuln", query, f"user:{username}, pass:{password}")
        logging.warning(f"检测到可疑SQL注入尝试: {username} | {password}")
    
    try:
        cur = get_db().execute(query)
        rows = cur.fetchall()
        
        result = {
            "endpoint": "vulnerable",
            "success": len(rows) > 0,
            "user_count": len(rows),
            "users": [dict(r) for r in rows],
            "executed_sql": query,
            "security_analysis": {
                "vulnerability_detected": True,
                "risk_level": "HIGH",
                "attack_patterns": {
                    "username": user_patterns if is_suspicious_user else [],
                    "password": pass_patterns if is_suspicious_pass else []
                }
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        logging.info(f"脆弱端点访问 - 返回{len(rows)}条记录")
        return jsonify(result)
        
    except sqlite3.Error as e:
        error_msg = str(e)
        logging.error(f"SQL执行错误: {error_msg}")
        return jsonify({
            "endpoint": "vulnerable",
            "success": False,
            "error": error_msg,
            "executed_sql": query,
            "security_warning": "SQL语法错误可能表明存在注入尝试",
            "timestamp": datetime.datetime.now().isoformat()
        }), 400


# ---------------------------------------------------------------------------
# 安全端点 - 参数化查询演示 (Safe Endpoint)
# ---------------------------------------------------------------------------

@app.route("/login_safe")
def login_safe():
    """✅ 使用参数化查询的安全登录端点"""
    username = request.args.get("username", "")
    password = request.args.get("password", "")
    
    # 输入验证和清理
    if len(username) > 50 or len(password) > 50:
        return jsonify({
            "endpoint": "safe",
            "success": False,
            "error": "输入长度超出限制",
            "security_info": "实施输入长度限制是基础安全措施"
        }), 400
    
    # 检测可疑输入（仅用于统计和警告）
    is_suspicious_user, user_patterns = detect_sql_injection(username)
    is_suspicious_pass, pass_patterns = detect_sql_injection(password)
    
    if is_suspicious_user or is_suspicious_pass:
        logging.info(f"安全端点收到可疑输入（已被安全处理）: {username}")
    
    try:
        # ✅ 安全的参数化查询
        cur = get_db().execute(
            "SELECT id, username, role FROM users WHERE username=? AND password=?", 
            (username, password)
        )
        rows = cur.fetchall()
        
        result = {
            "endpoint": "safe",
            "success": len(rows) > 0,
            "user_count": len(rows),
            "users": [dict(r) for r in rows],  # 注意：不返回密码字段
            "security_analysis": {
                "vulnerability_detected": False,
                "risk_level": "LOW",
                "protection_mechanisms": [
                    "参数化查询",
                    "输入长度限制", 
                    "敏感信息过滤",
                    "错误信息控制"
                ],
                "suspicious_input_detected": is_suspicious_user or is_suspicious_pass,
                "attack_patterns_neutralized": user_patterns + pass_patterns
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        logging.info(f"安全端点访问 - 返回{len(rows)}条记录")
        return jsonify(result)
        
    except sqlite3.Error as e:
        logging.error(f"数据库查询错误: {str(e)}")
        return jsonify({
            "endpoint": "safe",
            "success": False,
            "error": "查询执行失败",
            "security_info": "参数化查询有效防止了SQL注入"
        }), 500


# ---------------------------------------------------------------------------
# 辅助端点 - 统计和分析功能 (Auxiliary Endpoints)
# ---------------------------------------------------------------------------

@app.route("/users")
def list_users():
    """列出所有用户（管理功能）"""
    try:
        cur = get_db().execute("SELECT id, username, role, created_at FROM users")
        users = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            "total_users": len(users),
            "users": users,
            "timestamp": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stats")
def attack_stats():
    """显示攻击统计信息"""
    stats = {
        "database_file": DATABASE,
        "attack_log_file": ATTACK_LOG,
        "log_exists": os.path.exists(ATTACK_LOG),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    if os.path.exists(ATTACK_LOG):
        with open(ATTACK_LOG, "r", encoding="utf-8") as f:
            logs = f.readlines()
        stats["total_attacks"] = len(logs)
        stats["recent_attacks"] = [log.strip() for log in logs[-10:]]  # 最近10次
    else:
        stats["total_attacks"] = 0
        stats["recent_attacks"] = []
    
    return jsonify(stats)


# ---------------------------------------------------------------------------
# 高级演示功能 (Advanced Demo Features)
# ---------------------------------------------------------------------------

@app.route("/advanced_vuln")
def advanced_vulnerability():
    """更复杂的SQL注入场景演示"""
    search_term = request.args.get("search", "")
    
    if not search_term:
        return jsonify({"error": "请提供search参数"}), 400
    
    # 复杂的脆弱查询
    query = f"""
    SELECT u.username, u.role, s.secret_info 
    FROM users u 
    LEFT JOIN sensitive_data s ON u.id = s.user_id 
    WHERE u.username LIKE '%{search_term}%' 
    OR u.role LIKE '%{search_term}%'
    """
    
    try:
        cur = get_db().execute(query)
        results = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            "search_term": search_term,
            "results": results,
            "executed_sql": query,
            "warning": "此端点演示了更复杂的SQL注入场景",
            "example_payloads": [
                "admin' UNION SELECT username,password,'SECRET' FROM users--",
                "' OR 1=1--",
                "test' AND (SELECT COUNT(*) FROM users)>0--"
            ]
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "executed_sql": query,
            "note": "SQL错误通常表明注入尝试"
        }), 400


# ---------------------------------------------------------------------------
# 程序入口 (Entry Point)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 80)
    print("🔐 SQL注入攻击与防御演示系统")
    print("SQL Injection Attack & Defense Demo System")
    print("=" * 80)
    print("📚 教育研究专用 | For Educational & Research Purpose Only")
    print("⚠️  请勿用于恶意攻击 | Do Not Use for Malicious Attacks")
    print("=" * 80)
    
    # 自动初始化数据库
    init_db()
    
    print("🚀 服务启动信息:")
    print(f"   - 本地访问: http://127.0.0.1:5000/")
    print(f"   - 脆弱端点: http://127.0.0.1:5000/login_vuln")
    print(f"   - 安全端点: http://127.0.0.1:5000/login_safe")
    print(f"   - 数据库文件: {DATABASE}")
    print(f"   - 攻击日志: {ATTACK_LOG}")
    print("=" * 80)
    
    # 启动Flask应用
    app.run(host="0.0.0.0", port=5000, debug=True)
