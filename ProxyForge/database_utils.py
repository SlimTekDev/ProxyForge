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
    host = (os.environ.get("MYSQL_HOST") or "localhost").strip()
    password = (os.environ.get("MYSQL_PASSWORD") or "").strip()
    port_str = (os.environ.get("MYSQL_PORT") or "").strip()
    port = int(port_str) if port_str else 3306
    kwargs = dict(
        host=host,
        port=port,
        user=(os.environ.get("MYSQL_USER") or "root").strip(),
        password=password,
        database=(os.environ.get("MYSQL_DATABASE") or "wargaming_erp").strip(),
        autocommit=True,
        buffered=True,
        connection_timeout=10,
    )
    # DigitalOcean and other managed MySQL require SSL for remote connections
    if host not in ("localhost", "127.0.0.1"):
        kwargs["ssl_disabled"] = False
        if (os.environ.get("MYSQL_SSL_VERIFY") or "1").strip().lower() in ("0", "false", "no"):
            kwargs["ssl_verify_cert"] = False
    return mysql.connector.connect(**kwargs)
