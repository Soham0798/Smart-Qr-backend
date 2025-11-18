from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from passlib.hash import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .. import schemas, models, crud
from ..database import SessionLocal

SECRET_KEY = "secretkey123"  # move to .env later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = crud.get_user_by_username(db, username=username)
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not bcrypt.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}
