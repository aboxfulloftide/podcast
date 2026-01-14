from mysql.connector.connection import MySQLConnection
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def create_user(db: MySQLConnection, user: UserCreate):
    """
    Create a new user in the database.
    """
    cursor = db.cursor()
    hashed_password = get_password_hash(user.password)
    query = "INSERT INTO users (username, hashed_password) VALUES (%s, %s)"
    cursor.execute(query, (user.username, hashed_password))
    db.commit()
    user_id = cursor.lastrowid
    cursor.close()
    return {"id": user_id, "username": user.username}

def get_user_by_username(db: MySQLConnection, username: str):
    """
    Get a user from the database by username.
    """
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, username, hashed_password FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()
    return user
