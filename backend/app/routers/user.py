from fastapi import APIRouter, Depends, Response
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.serviced import UserService
from app.db.schemas.users import UserLogin, UserRead, UserCreate
from app.core.jwt_handler import get_password_hash
from app.core.auth import set_auth_cookies, get_user_id

router=APIRouter(prefix="/users",tags=["User"])

@router.post("/signup", response_model=UserRead)
async def signup(user:UserCreate, db:AsyncSession =  Depends(get_db)):
    db_user=await UserService.signup(db, user)
    return db_user

#Post에서 값 입력 -> userCreate로 검증 -> get_db세션주입 -> 
# UserService 사용해서(중복검사, 해싱, 저장, 커밋)-> UserRead로 변환


#users/login
#response : 쿠키를 심을 응답객체
@router.post("/login", response_model=UserRead)
async def login(user:UserLogin,response:Response, db:AsyncSession=Depends(get_db)):
    result=await UserService.login(db, user)
    db_user, access_token, refresh_token = result
    #토큰 두개를 쿠키로 응답에 붙인다
    set_auth_cookies(response, access_token, refresh_token)
    return db_user

#미들웨어 등록
@router.get("/me", response_model=UserRead)
async def get_user(user_id:int=Depends(get_user_id), db:AsyncSession=Depends(get_db)):
    return await UserService.get_user(db, user_id)

#로그아웃시 엑세스, 리프레시 토큰 쿠키 삭제
@router.post("/logout")
async def logout(response:Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return True