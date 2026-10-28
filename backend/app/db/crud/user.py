from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User, Todo, Hashtag
from app.db.schemas.users import UserCreate, HashCreate, TodoCreate


class UserCrud:
    @staticmethod
    async def get_by_id(db:AsyncSession, user_id:int) -> User | None:
        result = await db.execute(select(User).filter(User.user_id == user_id))
        return result.scalar_one_or_none()


    @staticmethod
    async def create(db:AsyncSession, user:UserCreate) -> User :
        #db삽입
        db_user=User(**user.model_dump())
        db.add(db_user)
        await db.flush()
        return db_user

    @staticmethod
    async def delete_by_id(db:AsyncSession, user_id:int) -> User | None:
        db_user=await db.get(User, user_id)
        if db_user:
            await db.delete(db_user)
            await db.flush()
            return db_user
        return None


    @staticmethod
    async def get_by_email(db:AsyncSession, email:str) -> User | None:
        result=await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()


    
    @staticmethod
    async def update_refresh_token_by_id(
        db:AsyncSession, user_id:int, refresh_token:str) :
        
        db_user=await db.get(User, user_id)
        if db_user:
            db_user.refresh_token=refresh_token
            await db.flush()
        return db_user

class HashCrud:
    @staticmethod
    async def create_hash(db:AsyncSession, hash:HashCreate) -> Hashtag:
        db_hash=Hashtag(hash.hashtag)
        db.add(db_hash)
        await db.flush(db_hash)
        return db_hash

class TodoCrud:
    @staticmethod
    async def create_todo(db:AsyncSession, todo:TodoCreate, user_id:int) -> Todo:
        db_todo = Todo(**todo.model_dump(), user_id=user_id)
        db.add(db_todo)
        await db.flush()
        return db_todo