import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg://postgres:postgres123@localhost:5432/mydb"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
