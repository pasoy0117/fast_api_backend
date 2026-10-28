from fastapi import APIRouter, Depends, Response
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.serviced import UserService, TodoService, HashService
from app.db.schemas.users import UserLogin, UserRead, UserCreate, TodoCreate, HashCreate
from app.core.jwt_handler import get_password_hash
from app.core.auth import set_auth_cookies, get_user_id

router=APIRouter(prefix="/users",tags=["User"])

@router.post("/signup", response_model=UserRead)
async def signup(user:UserCreate, db:AsyncSession =  Depends(get_db)):
    db_user=await UserService.signup(db, user)
    return db_user


@router.post("/login", response_model=UserRead)
async def login(user:UserLogin,response:Response, db:AsyncSession=Depends(get_db)):
    result=await UserService.login(db, user)
    db_user, access_token, refresh_token = result
    set_auth_cookies(response, access_token, refresh_token)
    return db_user


@router.get("/me", response_model=UserRead)
async def get_user(user_id:int=Depends(get_user_id), db:AsyncSession=Depends(get_db)):
    return await UserService.get_user(db, user_id)


@router.post("/logout")
async def logout(response:Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return True


@router.get("/user", response_model=UserRead)
async def get_all_user(user:UserRead):
    users=await UserService.get_user(user)
    return users

@router.get("/{user_id}", response_model=UserRead)
async def get_user_id(user_id:int, db:AsyncSession=Depends(get_db)):
    db_user=await UserService.get_user(db, user_id)
    return db_user

@router.delete("/{user_id}")
async def del_user(user_id:int, db:AsyncSession=Depends(get_db)):
    return await UserService.delete_user(db, user_id)

@router.post("/todo")
async def create_todo(todo:TodoCreate, user_id:int=Depends(get_user_id), db:AsyncSession=Depends(get_db)):
    return await TodoService.todo(db, todo, user_id)