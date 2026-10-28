from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from typing import Optional

#orm타입힌트 -> 새로운 타입 힌트방식 -> Mapped => 각필드의 특정타입을 좀 더 명확히 정의가능
class User(Base):
    __tablename__="users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] =mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] =mapped_column(String(300), nullable=False)
    refresh_token : Mapped[str]=mapped_column(String(255), nullable=True)
    created_at: Mapped[Optional[datetime]]= mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)

class Todo(Base):
    __tablename__='todos'

    todo_id:Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]=mapped_column(String(50), nullable=False)
    content:Mapped[str]=mapped_column(String(100), nullable=False)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.user_id"))

class hashtag(Base):
    __tablename__="hashtag"
    
    hashtag_id:Mapped[int]=mapped_column(primary_key=True)
    hashtag:Mapped[str]=mapped_column(String(50))

class todo_hashtag(Base):
    __tablename__="todo_hash"

    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.user_id"))
    hashtag_id:Mapped[int]=mapped_column(ForeignKey("hashtag.hashtag_id"))