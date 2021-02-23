import os
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel

load_dotenv(find_dotenv())


class PostgresDsl(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: int


postgres_dsl = PostgresDsl(dbname=os.getenv('DB_NAME', 'auth'),
                           user=os.getenv('DB_USER', 'postgres'),
                           password=os.getenv('DB_PASSWORD', '000'),
                           host=os.getenv('DB_HOST', 'localhost'),
                           port=os.getenv('DB_PORT', 5434))


SECRET_KEY = os.getenv('SECRET_KEY')


class Redis(BaseModel):
    host: str
    port: int
    db: int


redis_0_params = Redis(host=os.getenv('REDIS_HOST', 'localhost'),
                       port=os.getenv('REDIS_PORT', 6379),
                       db=os.getenv('REDIS_DB', 0))
redis_1_params = Redis(host=os.getenv('REDIS_HOST', 'localhost'),
                       port=os.getenv('REDIS_PORT', 6379),
                       db=os.getenv('REDIS_DB1', 1))


TOKEN_TIME = 60 * 5
PIN_CODE_TIME = 60
