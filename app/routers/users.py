from fastapi import APIRouter, Depends
from ..database import SessionLocal
from .. import schemas
from .auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=schemas.UserOut)
def get_current_user_details(user=Depends(get_current_user)):
    return user
