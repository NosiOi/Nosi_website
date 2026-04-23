import os


class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg://postgres:postgres123@localhost:5432/mydb"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
