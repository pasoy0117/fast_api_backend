from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User
from app.db.schemas.users import UserCreate, UserUpdate

#@staticmethod, @classbethod -> 인스턴스 없이 클래스에서 바로 호출
class UserCrud:
    @staticmethod
    async def get_by_id(db:AsyncSession, user_id:int) -> User | None:
        result = await db.execute(select(User).filter(User.user_id == user_id))
        return result.scalar_one_or_none() #결과가 0이면 none, 한개면 객체, 두개이상 에러


    @staticmethod
    async def create(db:AsyncSession, user:UserCreate) -> User :
        #db삽입
        db_user=User(**user.model_dump())
        db.add(db_user) #동기(await없음)
        await db.flush() #변경 사항을 isert로 db에 전송 -> commit을 안해서 롤백이 가능함(영구반영안함)
        return db_user

    @staticmethod
    async def delete_by_id(db:AsyncSession, user_id:int) -> User | None:
        db_user=await db.get(User, user_id)
        if db_user:
            await db.delete(db_user) #delete는 await을 걸어줘야함. cascade속성때문에. 아직 로드되지 않은 자식테이블의 경우db에서 불러와야함(동기식으로 막바로 지우면 안됨)
            await db.flush()       #delete from users user_id=(1)
            return db_user  #삭제된 객체 반환
        return None


    @staticmethod
    async def get_by_email(db:AsyncSession, email:str) -> User | None:
        result=await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()


    #리프레시 토큰을 왜 DB에 저장? -> 재사용 방지
    #오래 살아있기 때문에 유출되면 내가 아닌 제3자가 계속 새 엑세스 토큰을 발급 받을 수 있다.
    #보안 강화 -> 서버에서 검증하려고(db와 비교해서)

    #사용자 로그인 -> 새 리프레시 토큰 발급 -> db에 저장
    #엑세스가 만료되면 사용자가 리프레시 토큰을 전송
    #서버에서 db확인 후 리프레시 토큰이 일치하면 새 엑세스 토큰 발급, 
    #일치하지 않으면 새 엑세스 발급 거부
    @staticmethod
    async def update_refresh_token_by_id(
        db:AsyncSession, user_id:int, refresh_token:str) :
        
        db_user=await db.get(User, user_id) #기본키로 사용자 조회
        if db_user:
            db_user.refresh_token=refresh_token
            await db.flush()
            
        return db_user