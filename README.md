# DB Assistant - 数据库助手 (Claude Code Skill)

通用数据库操作助手，通过自然语言或命令行直接操作数据库。当前支持 MySQL/MariaDB，后续将兼容 PostgreSQL、SQLite 等多种数据库。

## 功能特性

- 🔍 **查询数据** - SELECT 查询，支持条件筛选
- ➕ **插入数据** - INSERT 插入新记录
- ✏️ **更新数据** - UPDATE 更新现有记录
- 🗑️ **删除数据** - DELETE 删除记录
- 📋 **表管理** - 查看表结构、列出所有表
- 🌐 **多数据库** - 支持配置多个数据库连接，未来将支持更多数据库
- 💬 **自然语言** - 支持中文自然语言触发

**当前支持：** MySQL、MariaDB  
**计划中：** PostgreSQL、SQLite、SQL Server

## 目录结构

```
db-assistant/
├── SKILL.md              # Skill 元数据（Claude Code 识别用）
├── README.md             # 本文档
├── config.json           # 配置文件（数据库连接）
├── scripts/
│   └── db_ops.py        # 数据库操作脚本
└── config.json.example   # 配置示例
```

## 安装

### 1. 安装到 Claude Code

将整个 `db-assistant` 目录复制到 Claude Code 的 skills 目录：

**Windows:**
```
C:\Users\<用户名>\.claude\skills\db-assistant
```

**macOS/Linux:**
```
~/.claude/skills/db-assistant
```

### 2. 安装 Python 依赖

```bash
# MySQL/MariaDB
pip install mysql-connector-python

# PostgreSQL（计划中）
# pip install psycopg2-binary

# SQLite（计划中）
# pip install sqlite3
```

### 3. 配置数据库连接

复制配置文件示例并编辑：

```bash
cp config.json.example config.json
```

编辑 `config.json`，填入你的数据库信息：

```json
{
  "connections": {
    "default": "mysql://用户名:密码@主机:端口/数据库名",
    "myapp": "mysql://appuser:password@192.168.1.100:3306/myapp",
    "production": "postgresql://produser:password@prod.example.com:5432/production"
  }
}
```

#### 连接字符串格式

| 数据库 | 格式 | 示例 |
|--------|------|------|
| MySQL/MariaDB | `mysql://用户:密码@主机:3306/数据库` | `mysql://root:pass@localhost:3306/mydb` |
| PostgreSQL（计划中） | `postgresql://用户:密码@主机:5432/数据库` | `postgresql://user:pass@localhost:5432/mydb` |
| SQLite（计划中） | `sqlite:///路径` | `sqlite:///path/to/db.sqlite` |
| SQL Server（计划中） | `mssql://用户:密码@主机:1433/数据库` | `mssql://user:pass@localhost:1433/mydb` |

## 使用方法

### 方法 1：自然语言（推荐）

在 Claude Code 中直接用自然语言描述操作：

```
帮我查询 users 表前 10 条数据
查询 test1 数据库的 orders 表
给 users 表插入一条记录，name 是张三，email 是 zhangsan@example.com
更新 users 表 id=1 的记录，把 name 改成李四
删除 users 表 id=1 的记录
查看 users 表的结构
列出所有表
```

### 方法 2：命令行

通过数据库 CLI 直接执行 SQL：

```bash
# MySQL
mysql -h 主机 -u 用户 -p 密码 数据库 -e "SQL 语句"

# PostgreSQL（计划中）
# psql -h 主机 -U 用户 -d 数据库 -c "SQL 语句"

# SQLite（计划中）
# sqlite3 /path/to/db.sqlite "SQL 语句"
```

### 方法 3：Python 脚本

```bash
python ~/.claude/skills/db-assistant/scripts/db_ops.py <命令> [参数]
```

#### 命令行参数

| 命令 | 用法 | 说明 |
|------|------|------|
| `tables` | `tables [连接名]` | 列出所有表 |
| `schema` | `schema <表名> [连接名]` | 查看表结构 |
| `query` | `query <SQL> [连接名]` | 执行查询 |
| `insert` | `insert <表名> <JSON> [连接名]` | 插入记录 |
| `update` | `update <表名> <WHERE> <JSON> [连接名]` | 更新记录 |
| `delete` | `delete <表名> <WHERE> [连接名]` | 删除记录 |

#### 示例

```bash
# 列出所有表（使用 default 连接）
python db_ops.py tables

# 列出所有表（使用 test1 连接）
python db_ops.py tables test1

# 查看表结构
python db_ops.py schema users

# 查询数据
python db_ops.py query "SELECT * FROM users LIMIT 10"

# 插入数据
python db_ops.py insert users '{"name": "张三", "email": "zhangsan@test.com"}'

# 更新数据
python db_ops.py update users "id=1" '{"name": "李四"}'

# 删除数据
python db_ops.py delete users "id=1"
```

## 自然语言触发词

当检测到以下句式时，自动激活此技能：

### 查询类（Read）
- "帮我查询 xxx 数据库"
- "查询一下 xxx 表"
- "我想查看 xxx 表的数据"
- "show me the users table"
- "select * from xxx"

### 插入类（Create）
- "插入一条数据到 xxx 表"
- "给 xxx 表添加一条记录"
- "insert into xxx"

### 更新类（Update）
- "更新 xxx 表的 xxx 记录"
- "修改 xxx 表的 xxx 数据"
- "update xxx set"

### 删除类（Delete）
- "删除 xxx 表的 xxx 记录"
- "从 xxx 表删除 xxx 数据"
- "delete from xxx where"

### 结构类
- "查看 xxx 表的结构"
- "列出所有表"
- "show tables"
- "describe xxx"

## 配置项说明

```json
{
  "connections": {
    "default": "mysql://...",
    "连接名": "连接字符串..."
  },
  "options": {
    "query_limit": 100,      // 查询结果条数限制
    "timeout": 30,           // 连接超时时间（秒）
    "ssl": false,            // 是否使用 SSL 连接
    "log_sql": true          // 是否打印执行的 SQL
  }
}
```

## 安全建议

1. **不要硬编码密码** - 使用 `config.json` 配置文件
2. **限制数据库权限** - 生产环境使用只读账号
3. **更新和删除带 WHERE** - 脚本会拒绝没有条件的 UPDATE/DELETE
4. **定期备份数据** - 执行危险操作前先备份

## 常见问题

### Q: 提示 "mysql-connector-python not installed"
```bash
pip install mysql-connector-python
```

### Q: 中文显示乱码
确保数据库连接使用 `utf8mb4` 字符集：
```python
mysql.connector.connect(
    ...
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci"
)
```

### Q: 连接失败
1. 检查 MySQL 服务是否运行
2. 检查端口是否正确（默认 3306）
3. 检查用户名密码是否正确
4. 检查防火墙是否开放端口

### Q: 如何连接多个数据库？
在 `config.json` 中添加多个连接：

```json
{
  "connections": {
    "default": "mysql://user:pass@localhost:3306/db1",
    "db2": "mysql://user:pass@localhost:3307/db2",
    "db3": "mysql://user:pass@192.168.1.100:3306/db3"
  }
}
```

使用：`查询 db2 的 users 表`

## 扩展开发

如需添加新功能（如 PostgreSQL 支持），修改 `scripts/db_ops.py`：

```python
def cmd_new_feature(args):
    """新功能说明"""
    # 实现代码
    pass

# 在 main() 函数中注册
elif cmd == "new_feature":
    cmd_new_feature(args)
```

## 协议

MIT License

## 作者

DB Assistant for Claude Code

## GitHub

仓库地址：<ADDRESS_REDACTED>
