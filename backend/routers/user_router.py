from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  
from database import get_db

router = APIRouter()
@router.get("/")
def read_users():
    return [{"message": "List of users"}]