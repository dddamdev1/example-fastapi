from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings

""" import os
from dotenv import load_dotenv

load_dotenv()

db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASS")
db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}" """

##SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password123@localhost:5432/fastapi"
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

## Reference Code to connect to Postgres DB
# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', 
#                                 password='password123', cursor_factory=RealDictCursor)
#         cursor= conn.cursor()
#         print("Database connection was successful")
#         break
#     except Exception as error:
#         print("Database connection failed")
#         print("Error", error)
#         time.sleep(2)

############################################################################################


