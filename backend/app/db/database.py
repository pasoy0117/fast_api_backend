from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from app.core.settings import settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

#비동기 db연결 생성하는 함수, (my sql+ayncmy url사용하여 비동기적으로db와 연결한다.)
async_engine=create_async_engine(settings.db_url, echo=False)

#위에서 만든 엔진과 연결
#비동기 -> db쿼리 기다리는 동안 서버가 다른 요청을 처리 할 수 있게 하기 위해서
#autocommit=False : 쿼리 실행 전, 변경사항을 자동으로 db에 보내는 작업 꺼놓음
AsyncSessionLocal=sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

#동기 DB연결 생성하는 함수
#pool_pre_ping=True : 연결 풀에서 꺼낼 때 마다 살아있는 연결인지 확인
sync_engine=create_engine(settings.sync_db_url, pool_pre_ping=True)

Base=declarative_base()
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session