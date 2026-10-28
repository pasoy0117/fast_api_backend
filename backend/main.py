import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, async_engine
from fastapi.concurrency import asynccontextmanager
from app.routers import user
from app.middleware.token_refresh import TokenRefreshMiddleware


load_dotenv(dotenv_path=".env")


#서버 켤때/끌때 할 일 정의
#서버가 시작 -> 테이블 생성 -> yeild (일시정지) -> 이후 엔진정리(db연결정리) -> 서버 종료
@asynccontextmanager
async def lifespan(app:FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield #서버가 켜져있는 동안 일시정지(안쓰면 시작하고 바로 꺼버림)
    await async_engine.dispose()


app=FastAPI(lifespan=lifespan)
app.add_middleware(TokenRefreshMiddleware) # 모든 요청이 미들웨어를 거치도록!

#미들웨어 : 모든 요청이 api함수에 도착하기 전, 응답이 나가기 전에 거치는 확인 작업!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

#user.py에 만든 라우터를 fastapi 앱에 등록함
app.include_router(user.router)

if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)