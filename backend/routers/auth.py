import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.auth.jwt import hash_password, verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])

USERS_FILE = "users.json"


def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


class RegisterRequest(BaseModel):
    user_id: str
    password: str


class LoginRequest(BaseModel):
    user_id: str
    password: str


@router.post("/register")
def register(request: RegisterRequest):
    users = load_users()

    if request.user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")

    users[request.user_id] = hash_password(request.password)
    save_users(users)

    return {"message": "User registered successfully"}


@router.post("/login")
def login(request: LoginRequest):
    users = load_users()

    if request.user_id not in users:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(request.password, users[request.user_id]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(request.user_id)
    return {"access_token": token, "token_type": "bearer"}