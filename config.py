import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'NOT_FOUND_SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL', 'NOT_FOUND_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'NOT_FOUND_SECRET_KEY')
    CORS_HEADERS = 'Content-Type'
