from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from mysql.connector.connection import MySQLConnection
from app.db.session import get_db_connection
from app.core.config import settings
from app.schemas.user import TokenData
from app.crud import crud_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login/access-token")

def get_db():
    """Get a database connection from the pool."""
    db_conn = None
    try:
        db_conn = next(get_db_connection())
        yield db_conn
    finally:
        if db_conn:
            db_conn.close()

async def get_current_user(
    db: MySQLConnection = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud_user.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user