from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Todo, Hashtag
from app.db.schemas.users import UserCreate, UserLogin, TodoCreate, HashCreate
from fastapi import HTTPException
from app.db.crud import UserCrud, TodoCrud, HashCrud
from app.core.jwt_handler import get_password_hash, verify_password, create_access_token, create_refresh_token

class UserService:

    #회원가입시, 같은 이름이 있는지 없는지 확인하려고 일단 이름 넣고 db조회함
    @staticmethod
    async def signup(db:AsyncSession, user:UserCreate) -> User :
        if await UserCrud.get_by_email(db, user.email):
            raise HTTPException(status_code=400, detail='이미 사용중인 사용자 이름이다.')

        hashed_pw=get_password_hash(user.password)
        user_info=UserCreate(email=user.email, password=hashed_pw)

        try:
            db_user=await UserCrud.create(db, user_info)
            await db.commit() #실질적으로 DB에 영구반영이 일어나는 위치. 마지막 업무 단위.(라우터 전)
            await db.refresh(db_user)
            return db_user
        except Exception:
            await db.rollback()
            raise

    #비밀번호와 내가 쓴 비번이랑 맞아야함
    #토큰을 생성 해 줘야 함
    @staticmethod
    async def login(db:AsyncSession, user:UserLogin) -> tuple :
        db_user=await UserCrud.get_by_email(db, user.email)
        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail='잘못된 이메일 또는 비밀번호')

        refresh_token=create_refresh_token(db_user.user_id)
        access_token = create_access_token(db_user.user_id)

        #db에 리프레시 토큰 저장
        updated_user=await UserCrud.update_refresh_token_by_id(db, db_user.user_id, refresh_token)
        await db.commit()
        await db.refresh(updated_user)
        return updated_user, access_token, refresh_token

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> dict:
        db_user = await UserCrud.get_by_id(db, user_id)

        if not db_user:
            raise HTTPException(status_code=404, detail="User Not Found" )

        try:
            await UserCrud.delete_by_id(db, user_id)
            await db.commit()

            return {"message": "회원 삭제 완료", "user_id": user_id}

        except Exception:
            await db.rollback()
            raise


    @staticmethod
    async def get_user(db:AsyncSession, user_id:int) -> User :
        db_user=await UserCrud.get_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User Not Found")
        return db_user

    @staticmethod
    async def get_all(db:AsyncSession) -> list[User]:
        return await UserCrud.get_all(db)

class TodoService:
    @staticmethod
    async def todo(db:AsyncSession, todo:TodoCreate, user_id:int) -> Todo:
        try:
            db_todo = await TodoCrud.create_todo(db, todo, user_id)
            await db.commit()
            await db.refresh(db_todo)
            return db_todo

        except Exception:
            await db.rollback()
            raise

class HashService:
    @staticmethod
    async def hash(db:AsyncSession, hash:HashCreate) -> Hashtag:
        db_hash=await HashCrud.create_hash(db, hash)
        await db.commit()
        await db.refresh(db_hash)
        return db_hash