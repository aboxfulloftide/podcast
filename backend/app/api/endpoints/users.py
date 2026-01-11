from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from mysql.connector.connection import MySQLConnection
from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.schemas import user

router = APIRouter()

@router.post("/register", response_model=user.User)
def register_user(
    *,
    db: MySQLConnection = Depends(deps.get_db),
    user_in: user.UserCreate,
):
    """
    Create new user.
    """
    db_gen = next(db)
    user = crud_user.get_user_by_username(db=db_gen, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud_user.create_user(db=db_gen, user=user_in)
    return user

@router.post("/login/access-token", response_model=user.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: MySQLConnection = Depends(deps.get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    db_gen = next(db)
    user = crud_user.get_user_by_username(db_gen, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
