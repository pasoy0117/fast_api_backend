from passlib.context import CryptContext
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from app.core.settings import settings

#사용할 해시 알고리즘 지정
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")


#db에 비밀번호를 그대로 저장-> db유출되면 비밀번호 다 노출됨..
def get_password_hash(password:str):
    #비밀번호를 utf-8로 인코딩한 후 72바이트로 자른다.
    truncate_password=password.encode('utf-8')[:72] #문자열 -> 바이트
    return pwd_context.hash(truncate_password)

#회원가입 -> 123@!!@# -> 해시 -> DB에 저장
#로그인 -> 비번입력 -> 같은 방식으로 해시 - DB에 넣은 해시랑 같냐?


def verify_password(plain_password:str, hashed_password:str)-> bool:
    truncated_pw=plain_password.encode('utf-8')[:72]
    return pwd_context.verify(truncated_pw, hashed_password) #해싱+비교


#uid: 토큰 주인(사용자 id)
#(createtoken(1, timedelta, {type="access", username="kim"}))
#헤더: 알고리즘 정보 / payload : 토큰에 담는 데이터 / 서명(서버가 만든것, 중간에 내용안바뀜(증명하는 인감역할))
def create_token(uid:int, expires_delta:timedelta, **kwargs) -> str:
    to_encode=kwargs.copy()
    expire=datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp":expire, "uid":uid})
    encoded_jwt=jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)

    return encoded_jwt

#uid(사용자 id)를 받아서, 만료시간짜리 access_token 만들어서 반환해줌
def create_access_token(uid:int)->str:
    return create_token(uid=uid, expires_delta=settings.access_token_expire_second)


#jti (jwt id): jwt표준에서 토큰 고유 ID 
# uuid.uuid4() : 겹치지 않는 무작위 고유 ID만들어주는 함수-> 호출할때마다 새로운 값 나옴
#리프레시 토큰 관리(재발급/ 로그아웃 시 무효화)
def create_refresh_token(uid:int)->str:
    return create_token(uid=uid, jti=str(uuid.uuid4()), expires_delta=settings.refresh_token_expire_second)


#서버가 클라이언트가 넘김 jwt토큰 확인(서명, 만료확인)
#토큰을 디코딩해서 payload를 딕셔너리로 반환 access_token: {"uid":1, "expires_delta":900}
def decode_token(token:str)->dict:
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )


#jwt받아서, 검증 통과하면 사용자 id(uid) 만 꺼내서 돌려줌 -> 사용자 id
def verify_token(token:str)->int:
    #ex) access_token: {"uid":1, "expires_delta":900}
    payload=decode_token(token)
    return payload.get("uid")