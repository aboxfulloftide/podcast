from mysql.connector import pooling
from app.core.config import settings

db_pool = pooling.MySQLConnectionPool(
    pool_name="podcast_pool",
    pool_size=5,
    pool_reset_session=True,
    host=settings.DB_HOST,
    database=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    port=settings.DB_PORT
)

def get_db_connection():
    """Get a connection from the pool."""
    try:
        connection = db_pool.get_connection()
        yield connection
    finally:
        connection.close()
