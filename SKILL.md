---
name: db-assistant
description: 通用数据库操作助手，支持通过自然语言执行增删改查操作。当前支持 MySQL/MariaDB，后续将兼容 PostgreSQL、SQLite 等数据库。当用户用中文或英文描述数据库操作时触发，例如："查询数据库"、"帮我查一下"、"插入数据"、"更新记录"、"删除数据"、"查看表结构"、"列出所有表"、"导出数据"、"备份表"、"查看查询历史"。常见触发句式包括：帮我查询xxx、查询一下xxx数据库、我想查看xxx表、给xxx表插入一条数据、更新xxx表的xxx记录、删除xxx表中的xxx数据、导出xxx表、备份xxx表、查看查询历史。
---

# 数据库助手 (DB Assistant)

## 概述

通过自然语言或命令直接操作数据库。支持增删改查（CRUD）、表列表查看、表结构查看、数据导出、查询历史、Schema 对比、备份恢复等操作。

**当前支持：** MySQL、MariaDB  
**计划中：** PostgreSQL、SQLite、SQL Server

## 触发识别

当用户说以下内容时，自动激活此技能：

**查询类（Read）**：
- "帮我查询 xxx 数据库"
- "查询一下 xxx 表"
- "我想查看 xxx 表的数据"
- "show me the users table"
- "select * from xxx"

**插入类（Create）**：
- "插入一条数据到 xxx 表"
- "给 xxx 表添加一条记录"
- "insert into xxx"

**更新类（Update）**：
- "更新 xxx 表的 xxx 记录"
- "修改 xxx 表的 xxx 数据"
- "update xxx set"

**删除类（Delete）**：
- "删除 xxx 表的 xxx 记录"
- "从 xxx 表删除 xxx 数据"
- "delete from xxx where"

**结构类**：
- "查看 xxx 表的结构"
- "列出所有表"
- "show tables"
- "describe xxx"

**高级功能**：
- "导出 xxx 表到 CSV"
- "备份 xxx 表"
- "查看查询历史"
- "分析慢查询"
- "对比两个数据库结构"

## 快速配置

### 1. 创建配置文件

在 `~/.claude/skills/db-assistant/config.json` 中配置连接：

```json
{
  "connections": {
    "default": "mysql://用户名:密码@主机:端口/数据库名",
    "production": "mysql://user:pass@prod-host:3306/proddb",
    "test": "mysql://user:pass@test-host:3306/testdb"
  }
}
```

### 2. 安装依赖

```bash
# MySQL/MariaDB
pip install mysql-connector-python

# PostgreSQL（计划中）
# pip install psycopg2-binary

# SQLite（计划中）
# pip install sqlite3
```

## 功能列表

### 基础操作

| 命令 | 说明 | 示例 |
|------|------|------|
| `tables [连接]` | 列出所有表 | `tables default` |
| `schema <表名> [连接]` | 查看表结构 | `schema users` |
| `query <SQL> [连接]` | 执行查询 | `query "SELECT * FROM users LIMIT 10"` |
| `insert <表> <JSON> [连接]` | 插入记录 | `insert users '{"name":"张三"}'` |
| `update <表> <条件> <JSON> [连接]` | 更新记录 | `update users "id=1" '{"name":"李四"}'` |
| `delete <表> <条件> [连接]` | 删除记录 | `delete users "id=1"` |

### 高级功能 ⭐

| 命令 | 说明 | 示例 |
|------|------|------|
| `explain <SQL> [连接]` | 慢查询分析（EXPLAIN） | `explain "SELECT * FROM users WHERE age > 18"` |
| `export <表/查询> <文件> [格式] [连接]` | 导出数据（CSV/JSON） | `export users backup.csv csv` |
| `history [数量]` | 查看查询历史 | `history 20` |
| `history_clear` | 清空查询历史 | `history_clear` |
| `diff <连接1> <连接2>` | 对比两个数据库结构 | `diff default test` |
| `backup <表> <文件> [连接]` | 备份表 | `backup users users_backup.json` |
| `restore <文件> [连接]` | 恢复表 | `restore users_backup.json` |

## 自然语言使用示例

### 查询数据

```
帮我查询 users 表前 10 条数据
查询 select * from orders where status='pending'
我想看看 products 表有哪些数据
```

### 插入数据

```
给 users 表插入一条记录，name 是张三，email 是 zhangsan@example.com
insert into products values (null, '产品A', 99.9)
```

### 更新数据

```
更新 users 表 id=1 的记录，把 name 改成李四
把 orders 表 status='pending' 的订单状态改成 'shipped'
```

### 删除数据

```
删除 users 表 id=1 的记录
从 products 表删除 name='测试商品' 的记录
```

### 查看表结构

```
查看 users 表的结构
describe products
列出所有表
```

### 高级功能示例

#### 慢查询分析
```
分析这个查询的性能：SELECT * FROM users WHERE age > 18 AND city='北京'
帮我 explain 这个 SQL：SELECT u.* FROM users u JOIN orders o ON u.id=o.user_id
```

#### 导出数据
```
导出 users 表到 CSV
把 orders 表导出到 backup.json
导出查询结果：SELECT * FROM users WHERE age > 18 到 old_users.csv
```

#### 查询历史
```
查看最近的查询历史
显示我最近执行过的 20 条 SQL
清空查询历史
```

#### Schema 对比
```
对比 default 和 test 两个数据库的结构差异
看看生产环境和测试环境的表结构有什么不同
```

#### 备份恢复
```
备份 users 表
恢复 users 表从 backup.json
```

## 命令行直接使用

### 通过 Python 脚本

```bash
python ~/.claude/skills/db-assistant/scripts/db_ops.py <命令> [参数]

# 基础操作
python db_ops.py tables
python db_ops.py schema users
python db_ops.py query "SELECT * FROM users LIMIT 10"
python db_ops.py insert users '{"name": "张三"}'
python db_ops.py update users "id=1" '{"name": "李四"}'
python db_ops.py delete users "id=1"

# 高级功能
python db_ops.py explain "SELECT * FROM users WHERE age > 18"
python db_ops.py export users backup.csv csv
python db_ops.py export "SELECT * FROM users WHERE age > 18" old_users.json json
python db_ops.py history 20
python db_ops.py history_clear
python db_ops.py diff default test
python db_ops.py backup users users_backup.json
python db_ops.py restore users_backup.json
```

## 查询历史功能

脚本会自动记录所有查询操作到 `~/.db-assistant/history.json`（最多保留 100 条）。

历史记录包含：
- 时间戳
- 执行的 SQL
- 使用的连接
- 返回的行数
- 执行耗时（毫秒）

查看历史：
```bash
python db_ops.py history      # 最近 10 条
python db_ops.py history 20   # 最近 20 条
```

清空历史：
```bash
python db_ops.py history_clear
```

## 数据导出功能

支持导出为 CSV 或 JSON 格式：

```bash
# 导出整张表（CSV 格式，默认）
python db_ops.py export users users.csv

# 导出整张表（JSON 格式）
python db_ops.py export users users.json json

# 导出查询结果（CSV）
python db_ops.py export "SELECT * FROM users WHERE age > 18" old_users.csv

# 导出查询结果（JSON）
python db_ops.py export "SELECT * FROM users WHERE age > 18" old_users.json json
```

## Schema 对比功能

对比两个数据库的结构差异：

```bash
# 对比 default 和 test 两个连接对应的数据库
python db_ops.py diff default test
```

对比内容包括：
- 缺失的表
- 表结构差异（字段类型、是否为空等）

## 备份恢复功能

### 备份表

```bash
# 备份 users 表到 JSON 文件
python db_ops.py backup users users_backup.json
```

备份文件包含：
- 表结构（字段定义）
- 表数据（所有行）

### 恢复表

```bash
# 从备份文件恢复 users 表
python db_ops.py restore users_backup.json
```

**注意：** 恢复会先删除已存在的表，然后重新创建并插入数据。

## 连接字符串格式

| 数据库 | 格式 | 示例 |
|--------|------|------|
| MySQL/MariaDB | `mysql://用户:密码@主机:3306/数据库` | `mysql://root:pass@localhost:3306/mydb` |
| PostgreSQL（计划中） | `postgresql://用户:密码@主机:5432/数据库` | `postgresql://user:pass@localhost:5432/mydb` |
| SQLite（计划中） | `sqlite:///路径` | `sqlite:///path/to/db.sqlite` |

## 安全提示

- 更新和删除操作必须包含 WHERE 条件
- 执行破坏性操作前建议先备份数据
- 避免在命令中硬编码密码，使用 config.json 配置文件
- 生产环境建议创建专用数据库用户并限制权限
- 查询历史文件（`~/.db-assistant/history.json`）可能包含敏感 SQL，请妥善保管

## 支持的数据库

| 数据库 | 连接串前缀 | 状态 |
|--------|-----------|------|
| MySQL | `mysql://` | ✅ 完全支持 |
| MariaDB | `mysql://` | ✅ 兼容 |
| PostgreSQL | `postgresql://` | 🚧 计划中 |
| SQLite | `sqlite://` | 🚧 计划中 |
| SQL Server | `mssql://` | 🚧 计划中 |

## 故障排查

### 连接失败

```
ERROR: mysql.connector.errors.InterfaceError: ...
```

检查：
1. 数据库服务是否运行
2. 连接参数是否正确（主机、端口、用户名、密码）
3. 防火墙是否允许连接
4. 用户是否有远程连接权限

### 中文乱码

脚本已自动处理 UTF-8 编码。如果仍有乱码，检查：
1. 数据库字符集是否为 utf8mb4
2. 终端是否支持 UTF-8

### 查询历史不工作

检查 `~/.db-assistant/` 目录权限：
```bash
ls -la ~/.db-assistant/
```

## 更新日志

### v1.1.0 (2026-04-30)
- ✅ 新增：查询历史记录功能
- ✅ 新增：数据导出功能（CSV/JSON）
- ✅ 新增：慢查询分析（EXPLAIN）
- ✅ 新增：Schema 对比功能
- ✅ 新增：备份/恢复功能
- ✅ 优化：查询执行时间统计

### v1.0.0 (2026-04-30)
- ✅ 初始版本：基础 CRUD 操作
- ✅ 支持 MySQL/MariaDB
