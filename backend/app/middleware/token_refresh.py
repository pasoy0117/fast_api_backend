#요청이 올 때 마다 access_token이 만료됐는지 확인
#만료됐으면 refresh_token으로 새 토큰 발급해서 쿠키를 갱신하기 위함

#요청 도착 -> access_token 쿠키 확인 -> 만료 됐으면 -> refresh_token 확인 -> db에 새 refresh_token 저장하고 응답에 새 쿠키 심기
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from jwt import ExpiredSignatureError, InvalidTokenError
from app.db.database import get_db
from app.core.jwt_handler import verify_token, create_access_token, create_refresh_token
from app.core.auth import set_auth_cookies
from app.db.crud.user import UserCrud


#미들웨어 : 중개역할. 요청이 들어올 때, 응답이 나가기 전에 체크하기를 원함.
#/users/signup -> 회원가입 한 루 내 정보들을 response에 담음
#쿠키는 서버가 응답헤더에 실어서 브라우저(클라이언트)에 보낸다.
class TokenRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request:Request, call_next): #오버라이드
        #요청이 라우터로 가기 직전
        response=await call_next(request) #라우터를 실행해서 응답 받아두려고. request : 요청
        #응답 나가기 전
        #쿠키에 데이터를 담아 받으려면 응답 객체가 필요함.

        #브라우저가 보낸 쿠키에서 토큰들을 꺼냄
        access_token=request.cookies.get("access_token")
        refresh_token=request.cookies.get("refresh_token")

        try:
            if access_token:
                verify_token(access_token)
                return response
        except (ExpiredSignatureError, InvalidTokenError):
            pass


        if refresh_token:
            try:
                user_id = verify_token(refresh_token)
            except (ExpiredSignatureError, InvalidTokenError):
                return response
            except (ExpiredSignatureError):
                return JSONResponse(
                    status_code=401,
                    content={"detail" : "refresh_token_expired"}
                )

            new_access_token = create_access_token(user_id)
            new_refresh_token = create_refresh_token(user_id)

            try:
                db = await anext(get_db())
                await UserCrud.update_refresh_token_by_id(db, user_id, new_refresh_token)
                await db.commit()
            except Exception:
                await db.rollback()
                raise

            set_auth_cookies(response, new_access_token, new_refresh_token)

        return response

#요청 -> 라우터 실핼해서 응답 확보 -> 엑세스 토큰 확인 -> 유효하면 그대로 반환
             #      리프레시 토큰 유효-> 새 토큰 두개 다시 발급받아야함-> DB에 저장 -> 응답에 새 쿠키 -> 반환