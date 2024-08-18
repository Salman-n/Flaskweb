import os

class Config:
    SECRET_KEY = 'f23a9e1c4b2c8d3a87e3cbd63b2c7f7e'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:isal@localhost/test'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
