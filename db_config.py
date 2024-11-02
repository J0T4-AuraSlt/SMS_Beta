import psycopg2
from psycopg2 import pool
import logging

logger = logging.getLogger(__name__)

# Configuración del pool de conexiones
db_pool = pool.SimpleConnectionPool(
    1, 10,  # Mínimo y máximo de conexiones en el pool
    host='aurasolutions.c1yaeyakumzl.us-east-2.rds.amazonaws.com',
    database='DB_Test',
    user='AdminAura',
    password='Aur4S0lu71oN!'
)


def get_db_connection():
    """Obtiene una conexión del pool."""
    try:
        conn = db_pool.getconn()
        return conn
    except Exception as e:
        logger.error("Error al obtener conexión de la base de datos: %s", e)
        return None


def release_db_connection(conn):
    """Libera la conexión de vuelta al pool."""
    try:
        db_pool.putconn(conn)
    except Exception as e:
        logger.error("Error al liberar la conexión: %s", e)
