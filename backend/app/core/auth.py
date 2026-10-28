from fastapi import Request, Response, HTTPException
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.settings import settings
from typing import Optional
from app.core.jwt_handler import verify_token



def set_auth_cookies(response:Response, access_token:str, refresh_token:str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
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


async def get_user_id_optional(requeset:Request) -> Optional[int] :
    access_token=requeset.cookies.get("access_token")
    if not access_token:
        return None
    try:
        return verify_token(access_token)
    except( ExpiredSignatureError, InvalidTokenError):
        return None
    