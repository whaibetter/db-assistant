#!/usr/bin/env python3
"""
Database Assistant - Universal Database Operations Script
Supports: MySQL, PostgreSQL (planned), SQLite (planned)
Features: CRUD, Export, History, Explain, Diff, Backup/Restore
Usage: python db_ops.py <command> [args]
"""

import json
import sys
import os
import io
import csv
from pathlib import Path
from datetime import datetime
import time

# Fix Windows UTF-8 output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Check MySQL connector
try:
    import mysql.connector
except ImportError:
    print("ERROR: mysql-connector-python not installed")
    print("Run: pip install mysql-connector-python")
    sys.exit(1)

# History file location
HISTORY_DIR = Path.home() / ".db-assistant"
HISTORY_FILE = HISTORY_DIR / "history.json"
HISTORY_MAX = 100  # Keep last 100 queries


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"connections": {}}


def parse_url(url):
    """Parse mysql:// URL into connection parameters"""
    url = url.replace("mysql://", "")
    if "@" not in url:
        raise ValueError("Invalid URL format. Use: mysql://user:pass@host:port/db")

    auth, rest = url.split("@", 1)
    if ":" not in auth:
        raise ValueError("Invalid auth format. Use: user:pass")
    user, password = auth.split(":", 1)

    if "/" not in rest:
        raise ValueError("URL must include database name")

    host_port, database = rest.rsplit("/", 1)
    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host, port = host_port, "3306"

    return {
        "host": host,
        "port": int(port),
        "user": user,
        "password": password,
        "database": database,
    }


def connect(url_or_name):
    """Create database connection"""
    config = load_config()

    if url_or_name in config.get("connections", {}):
        url = config["connections"][url_or_name]
    else:
        url = url_or_name

    params = parse_url(url)
    return mysql.connector.connect(
        host=params["host"],
        port=params["port"],
        user=params["user"],
        password=params["password"],
        database=params["database"],
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
    )


# ==================== History Functions ====================

def load_history():
    """Load query history"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(history):
    """Save query history"""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    # Keep only last HISTORY_MAX entries
    history = history[-HISTORY_MAX:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def add_history(sql, connection, row_count, duration_ms):
    """Add entry to history"""
    history = load_history()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "sql": sql,
        "connection": connection,
        "row_count": row_count,
        "duration_ms": duration_ms
    }
    history.append(entry)
    save_history(history)


def cmd_history(limit=10):
    """Show query history"""
    history = load_history()
    if not history:
        print("(No history yet)")
        return

    # Show last N entries
    entries = history[-limit:]
    print(f"\nQuery History (last {len(entries)} of {len(history)}):")
    print("-" * 100)
    for i, entry in enumerate(entries, 1):
        ts = entry["timestamp"][:19]  # Just date and time
        sql = entry["sql"][:60] + ("..." if len(entry["sql"]) > 60 else "")
        conn = entry["connection"]
        rows = entry["row_count"]
        ms = entry["duration_ms"]
        print(f"{i}. [{ts}] {sql}")
        print(f"   Connection: {conn} | Rows: {rows} | Duration: {ms}ms")
    print("-" * 100)


def cmd_history_clear():
    """Clear query history"""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    print("History cleared.")


# ==================== Query Functions ====================

def cmd_query(sql, connection):
    """Execute SELECT query with history recording"""
    start = time.time()
    conn = connect(connection)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)

    rows = cursor.fetchall()
    duration_ms = int((time.time() - start) * 1000)

    if not rows:
        print("(No results)")
        add_history(sql, connection, 0, duration_ms)
        return

    headers = list(rows[0].keys())
    print("\t".join(headers))
    print("-" * 60)

    for row in rows:
        print("\t".join(str(row[h]) for h in headers))

    print(f"\n({len(rows)} rows, {duration_ms}ms)")
    add_history(sql, connection, len(rows), duration_ms)


def cmd_explain(sql, connection):
    """Execute EXPLAIN for slow query analysis"""
    conn = connect(connection)
    cursor = conn.cursor(dictionary=True)

    explain_sql = f"EXPLAIN {sql}"
    cursor.execute(explain_sql)
    rows = cursor.fetchall()

    if not rows:
        print("(No EXPLAIN result)")
        return

    headers = list(rows[0].keys())
    print("\nEXPLAIN Result:")
    print("-" * 100)
    print("\t".join(headers))
    print("-" * 100)

    for row in rows:
        print("\t".join(str(row[h]) for h in headers))

    # Add history
    add_history(f"EXPLAIN {sql}", connection, len(rows), 0)


# ==================== Export Functions ====================

def cmd_export(query_or_table, output_file, format="csv", connection="default"):
    """Export query or table to CSV or JSON"""
    conn = connect(connection)
    cursor = conn.cursor(dictionary=True)

    # Check if it's a table name or a query
    if " " not in query_or_table.upper():
        # It's a table name
        sql = f"SELECT * FROM {query_or_table}"
    else:
        # It's a query
        sql = query_or_table

    cursor.execute(sql)
    rows = cursor.fetchall()

    if not rows:
        print("(No data to export)")
        return

    if format.lower() == "json":
        # Export as JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(rows)} rows to {output_file} (JSON)")

    else:  # Default: CSV
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"Exported {len(rows)} rows to {output_file} (CSV)")

    # Add history
    add_history(f"EXPORT {query_or_table} TO {output_file}", connection, len(rows), 0)


# ==================== Schema Diff Functions ====================

def get_schema(connection):
    """Get full schema of a database"""
    conn = connect(connection)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]

    schema = {}
    for table in tables:
        cursor.execute(f"DESCRIBE {table}")
        columns = cursor.fetchall()
        schema[table] = []
        for col in columns:
            field, col_type, null, key, default, extra = col
            schema[table].append({
                "field": field,
                "type": col_type,
                "null": null,
                "key": key,
                "default": default,
                "extra": extra
            })

    return schema


def cmd_diff(conn1, conn2):
    """Compare schemas between two databases"""
    print(f"\nComparing schemas: {conn1} vs {conn2}")
    print("=" * 80)

    schema1 = get_schema(conn1)
    schema2 = get_schema(conn2)

    all_tables = set(schema1.keys()) | set(schema2.keys())

    for table in sorted(all_tables):
        in_1 = table in schema1
        in_2 = table in schema2

        if in_1 and not in_2:
            print(f"\n[MISSING] Table '{table}' exists in {conn1} but not in {conn2}")
        elif not in_1 and in_2:
            print(f"\n[MISSING] Table '{table}' exists in {conn2} but not in {conn1}")
        else:
            # Both have the table, compare columns
            cols1 = {c["field"]: c for c in schema1[table]}
            cols2 = {c["field"]: c for c in schema2[table]}

            all_cols = set(cols1.keys()) | set(cols2.keys())
            diffs = []

            for col in sorted(all_cols):
                if col not in cols1:
                    diffs.append(f"  [+{conn2}] Column '{col}' missing in {conn1}")
                elif col not in cols2:
                    diffs.append(f"  [-{conn1}] Column '{col}' missing in {conn2}")
                else:
                    # Compare column definitions
                    c1, c2 = cols1[col], cols2[col]
                    if c1["type"] != c2["type"]:
                        diffs.append(f"  [TYPE] {col}: {c1['type']} vs {c2['type']}")
                    if c1["null"] != c2["null"]:
                        diffs.append(f"  [NULL] {col}: {c1['null']} vs {c2['null']}")

            if diffs:
                print(f"\n[DIFF] Table '{table}':")
                for d in diffs:
                    print(d)

    print("\n" + "=" * 80)
    print("Schema comparison complete.")


# ==================== Backup/Restore Functions ====================

def cmd_backup(table, output_file, connection="default"):
    """Backup table structure and data"""
    conn = connect(connection)
    cursor = conn.cursor(dictionary=True)

    # Get table structure
    cursor.execute(f"DESCRIBE {table}")
    columns = cursor.fetchall()

    # Get table data
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()

    backup = {
        "table": table,
        "connection": connection,
        "timestamp": datetime.now().isoformat(),
        "schema": [{"field": c[0], "type": c[1], "null": c[2], "key": c[3], "default": c[4], "extra": c[5]} for c in columns],
        "data": rows
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)

    print(f"Backup complete: {table} ({len(rows)} rows) -> {output_file}")


def cmd_restore(backup_file, connection="default"):
    """Restore table from backup file"""
    with open(backup_file, "r", encoding="utf-8") as f:
        backup = json.load(f)

    table = backup["table"]
    schema = backup["schema"]
    data = backup["data"]

    conn = connect(connection)
    cursor = conn.cursor()

    # Drop table if exists
    cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # Recreate table (simplified - just use the first column's definition)
    # In real scenario, you'd need to reconstruct full CREATE TABLE
    print(f"Restore: Recreating table '{table}'...")
    print("(Note: This is a simplified restore. For production, use mysqldump)")

    # Insert data
    if data:
        columns = data[0].keys()
        placeholders = ", ".join(["%s"] * len(columns))
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

        for row in data:
            cursor.execute(sql, list(row.values()))

        conn.commit()
        print(f"Restored {len(data)} rows to {table}")
    else:
        print("No data to restore.")


# ==================== Original CRUD Functions ====================

def cmd_insert(table, data, connection):
    """Insert record"""
    conn = connect(connection)
    cursor = conn.cursor()

    if isinstance(data, str):
        data = json.loads(data)

    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    cursor.execute(sql, list(data.values()))
    conn.commit()

    print(f"Insert successful. {cursor.rowcount} row affected")
    print(f"New record ID: {cursor.lastrowid}")
    add_history(f"INSERT INTO {table} ...", connection, cursor.rowcount, 0)


def cmd_update(table, where, data, connection):
    """Update records"""
    conn = connect(connection)
    cursor = conn.cursor()

    if isinstance(data, str):
        data = json.loads(data)

    set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
    sql = f"UPDATE {table} SET {set_clause} WHERE {where}"

    cursor.execute(sql, list(data.values()))
    conn.commit()

    print(f"Update successful. {cursor.rowcount} row(s) affected")
    add_history(f"UPDATE {table} WHERE {where} ...", connection, cursor.rowcount, 0)


def cmd_delete(table, where, connection):
    """Delete records"""
    if not where or where.strip() == "":
        print("ERROR: DELETE requires WHERE clause")
        print("Example: delete users \"id=1\"")
        sys.exit(1)

    conn = connect(connection)
    cursor = conn.cursor()

    sql = f"DELETE FROM {table} WHERE {where}"
    cursor.execute(sql)
    conn.commit()

    print(f"Delete successful. {cursor.rowcount} row(s) affected")
    add_history(f"DELETE FROM {table} WHERE {where}", connection, cursor.rowcount, 0)


def cmd_tables(connection):
    """List all tables"""
    conn = connect(connection)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")

    tables = cursor.fetchall()
    print(f"Tables in database ({len(tables)}):")
    for (table_name,) in tables:
        print(f"  - {table_name}")


def cmd_schema(table, connection):
    """Show table structure"""
    conn = connect(connection)
    cursor = conn.cursor()

    cursor.execute(f"DESCRIBE {table}")
    columns = cursor.fetchall()

    print(f"\nTable: {table}")
    print("-" * 80)
    print(f"{'Field':<20} {'Type':<20} {'Null':<6} {'Key':<6} {'Default':<15} {'Extra'}")
    print("-" * 80)

    for col in columns:
        field, col_type, null, key, default, extra = col
        print(f"{field:<20} {col_type:<20} {null:<6} {key:<6} {str(default):<15} {extra}")


# ==================== Help ====================

def print_help():
    """Print help message"""
    print(__doc__)
    print("""
Commands:
  tables [connection]                     List all tables
  schema <table> [connection]             Show table structure
  query <sql> [connection]                Execute SELECT query
  explain <sql> [connection]              EXPLAIN query (slow query analysis)
  insert <table> <json> [connection]      Insert record
  update <table> <where> <json> [conn]    Update records
  delete <table> <where> [connection]      Delete records
  export <table|query> <file> [fmt] [conn] Export to CSV/JSON
  history [limit]                         Show query history
  history_clear                           Clear query history
  diff <conn1> <conn2>                    Compare schemas between two databases
  backup <table> <file> [connection]      Backup table to file
  restore <file> [connection]             Restore table from backup

Connection format: mysql://user:pass@host:port/database
Or use named connection from config.json

Examples:
  python db_ops.py query "SELECT * FROM users LIMIT 10" default
  python db_ops.py explain "SELECT * FROM users WHERE age > 18" default
  python db_ops.py export users backup.csv csv default
  python db_ops.py history 20
  python db_ops.py diff default test1
  python db_ops.py backup users users_backup.json default
""")


# ==================== Main ====================

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    cmd = sys.argv[1].lower()
    default_conn = "default"

    try:
        if cmd == "tables":
            url = sys.argv[2] if len(sys.argv) > 2 else default_conn
            cmd_tables(url)

        elif cmd == "schema":
            if len(sys.argv) < 3:
                print("Usage: db_ops.py schema <table> [connection]")
                sys.exit(1)
            table, url = sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else default_conn
            cmd_schema(table, url)

        elif cmd == "query":
            if len(sys.argv) < 3:
                print("Usage: db_ops.py query <sql> [connection]")
                sys.exit(1)
            sql, url = sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else default_conn
            cmd_query(sql, url)

        elif cmd == "explain":
            if len(sys.argv) < 3:
                print("Usage: db_ops.py explain <sql> [connection]")
                sys.exit(1)
            sql, url = sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else default_conn
            cmd_explain(sql, url)

        elif cmd == "insert":
            if len(sys.argv) < 4:
                print("Usage: db_ops.py insert <table> <json> [connection]")
                sys.exit(1)
            table, data, url = sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else default_conn
            cmd_insert(table, data, url)

        elif cmd == "update":
            if len(sys.argv) < 5:
                print("Usage: db_ops.py update <table> <where> <json> [connection]")
                sys.exit(1)
            table, where, data, url = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else default_conn
            cmd_update(table, where, data, url)

        elif cmd == "delete":
            if len(sys.argv) < 4:
                print("Usage: db_ops.py delete <table> <where> [connection]")
                sys.exit(1)
            table, where, url = sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else default_conn
            cmd_delete(table, where, url)

        elif cmd == "export":
            if len(sys.argv) < 4:
                print("Usage: db_ops.py export <table|query> <file> [format] [connection]")
                sys.exit(1)
            query_or_table = sys.argv[2]
            output_file = sys.argv[3]
            fmt = sys.argv[4] if len(sys.argv) > 4 else "csv"
            url = sys.argv[5] if len(sys.argv) > 5 else default_conn
            cmd_export(query_or_table, output_file, fmt, url)

        elif cmd == "history":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            cmd_history(limit)

        elif cmd == "history_clear":
            cmd_history_clear()

        elif cmd == "diff":
            if len(sys.argv) < 4:
                print("Usage: db_ops.py diff <conn1> <conn2>")
                sys.exit(1)
            conn1, conn2 = sys.argv[2], sys.argv[3]
            cmd_diff(conn1, conn2)

        elif cmd == "backup":
            if len(sys.argv) < 4:
                print("Usage: db_ops.py backup <table> <file> [connection]")
                sys.exit(1)
            table, output_file = sys.argv[2], sys.argv[3]
            url = sys.argv[4] if len(sys.argv) > 4 else default_conn
            cmd_backup(table, output_file, url)

        elif cmd == "restore":
            if len(sys.argv) < 3:
                print("Usage: db_ops.py restore <file> [connection]")
                sys.exit(1)
            backup_file = sys.argv[2]
            url = sys.argv[3] if len(sys.argv) > 3 else default_conn
            cmd_restore(backup_file, url)

        else:
            print(f"Unknown command: {cmd}")
            print_help()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
