"""
Manejador de conexiones pyodbc — una función por base de datos.
"""

import pyodbc

from mcp_db_agent.config.settings import DatabaseSettings


def crear_conexion(db_settings: DatabaseSettings) -> pyodbc.Connection:
    return pyodbc.connect(db_settings.connection_string(), timeout=10)