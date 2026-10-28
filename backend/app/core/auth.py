from fastapi import Request, Response, HTTPException
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.settings import settings
from typing import Optional
from app.core.jwt_handler import verify_token


#JWT토큰을 쿠키로 설정하려고
#httponly=True : 쿠키를 만들면 js에서 접근 불가(xss공격방어)
#samesite="Lax" : 외부 도메인 요청 시 쿠키 전송 제한됨

#로그인 성공하면 토큰을 쿠키에 심어서 요청이 올 떄 마다 쿠키로 누구인지 확인 할 것이다.
def set_auth_cookies(response:Response, access_token:str, refresh_token:str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token, #쿠키에 담을 문자열
        max_age=int(settings.access_token_expire_second),
        secure=False,
        httponly=True,
        samesite="Lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=int(settings.refresh_token_expire_second),
        secure=False,
        httponly=True,
        samesite="Lax",
    )

#로그인 할 때 토큰 검사
async def get_user_id(request:Request) -> int:
    access_token=request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail='Access token missing')

    try:
        user_id=verify_token(access_token)
        if user_id is None:
            raise HTTPException(status_code=401, detail='No UID')
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Access token expired')
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token error')

#모든 api가 로그인이 필수는 아니기 때문에
#로그인 안 한 사람도 접근 할 수 있게 하기 위해
async def get_user_id_optional(requeset:Request) -> Optional[int] :
    access_token=requeset.cookies.get("access_token")
    if not access_token:
        return None
    try:
        return verify_token(access_token)
    except( ExpiredSignatureError, InvalidTokenError):
        return None
    