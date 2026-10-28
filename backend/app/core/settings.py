from pydantic_settings import BaseSettings
from pydantic import Field
from datetime import timedelta

#.env에서 DB접속정보 읽어 접속 만들어주는 설정 클래스
class Settings(BaseSettings):
    db_user:str=Field(..., alias="DB_USER")
    db_password:str=Field(..., alias="DB_PASSWORD")
    db_host:str=Field("localhost", alias="DB_HOST")
    db_port:str=Field("3306", alias="DB_PORT")
    db_name:str=Field(..., alias="DB_NAME")

    #.env에서 토큰에 서명할 때 쓸 값
    secret_key:str=Field(..., alias="SECRET_KEY")
    jwt_algorithm:str=Field(..., alias="JWT_ALGORITHM")
    access_token_expire_second:int=Field(900, alias="ACCESS_TOKEN_EXPIRE")
    refresh_token_expire_second:int=Field(604800, alias="REFRESH_TOKEN_EXPIRE")


    class Config:  
        env_file=".env"
        case_sensitive=True  # 환경변수 이름 대소문자를 구분
        extra="allow"   # 모델에 정의되지 않은 추가 필드도 허용
        populate_by_name=True #필드 이름과 alias로 값을 채울 수 있음

    #메소드를 괄호 없이 속성처럼 쓸 수 있게 해 줌
    @property
    def tmp_db(self) -> str:  #"root:12345@localhost:3306/board"
        return f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property        #비동기 DB URL
    def db_url(self) -> str: #"mysql+asyncmy://root:12345@localhost:3306/board"
        return f"mysql+asyncmy://{self.tmp_db}"
    
    @property  #동기 DB URL
    def sync_db_url(self) -> str:
        return f"mysql+pymysql://{self.tmp_db}"

    ###################################################
    
    #초단위 정수값을 timedelta객체로 바꿔서 돌려줌 -> 토큰 만료시간 계산할 떄 바로 더할 수 있게 하기 위해
    @property
    def access_token_expire (self) -> timedelta:
        return timedelta(seconds=self.access_token_expire_second)

    @property
    def refresh_token_expire (self) -> timedelta:
        return timedelta(seconds=self.refresh_token_expire_second)

#전역 설정
settings=Settings()


