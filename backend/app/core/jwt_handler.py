from passlib.context import CryptContext
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from app.core.settings import settings


pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password:str): 
    truncate_password=password.encode('utf-8')[:72] 
    return pwd_context.hash(truncate_password)



def verify_password(plain_password:str, hashed_password:str)-> bool:
    truncated_pw=plain_password.encode('utf-8')[:72]
    return pwd_context.verify(truncated_pw, hashed_password) 



def create_token(uid:int, expires_delta:timedelta, **kwargs) -> str:
    to_encode=kwargs.copy()
    expire=datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp":expire, "uid":uid})
    encoded_jwt=jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)

    return encoded_jwt


def create_access_token(uid:int)->str:
    return create_token(uid=uid, expires_delta=settings.access_token_expire_second)



def create_refresh_token(uid:int)->str:
    return create_token(uid=uid, jti=str(uuid.uuid4()), expires_delta=settings.refresh_token_expire_second)




def decode_token(token:str)->dict:
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )



def verify_token(token:str)->int:
    payload=decode_token(token)
    return payload.get("uid")