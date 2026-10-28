from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated


class UserBase(BaseModel):
    email: str
    username: str
    password: str

class UserCreate(BaseModel):
    email: str
    username: str
    password: Annotated[str, Field(max_length=72)]

class UserLogin(BaseModel):
    email: str
    password: Annotated[str, Field(max_length=72)]


class UserUpdate(BaseModel):
    email: str | None = None
    username: str | None = None
    password: str | None = None


    #default_factory : 객체를 만들 때 마다 호출 -> 매번 현재시각이 들어감
class UserInDB(UserBase):
    user_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    #orm 객체를 pydantic모델로 변환할 수 있게 허용하는 옵션
    #db조회결과는 딕셔너리가 아니라 User orm 객체이므로
    class Config:
        from_attributes = True


class UserRead(UserInDB):
    pass