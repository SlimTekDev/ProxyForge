"""Database connection for ProxyForge. Reads config from environment (see repo .env.example)."""
import os

try:
    from dotenv import load_dotenv
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(_repo_root, ".env"))
except ImportError:
    pass

import mysql.connector


def get_db_connection():
    password = (os.environ.get("MYSQL_PASSWORD") or "").strip()
    port_str = (os.environ.get("MYSQL_PORT") or "").strip()
    port = int(port_str) if port_str else 3306
    return mysql.connector.connect(
        host=(os.environ.get("MYSQL_HOST") or "localhost").strip(),
        port=port,
        user=(os.environ.get("MYSQL_USER") or "root").strip(),
        password=password,
        database=(os.environ.get("MYSQL_DATABASE") or "wargaming_erp").strip(),
        autocommit=True,
        buffered=True,
        connection_timeout=10,
    )
