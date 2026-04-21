import os


class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:yarikpostNosiFitwebsite64ff@localhost:5432/nosifit"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
