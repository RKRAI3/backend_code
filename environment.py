import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'NOT_FOUND_SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL', 'NOT_FOUND_DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'NOT_FOUND_SECRET_KEY')
ADMIN_NAME = os.getenv('ADMIN_NAME', None)
ADMIN_ID = os.getenv('ADMIN_ID', None)
PASSWORD = os.getenv('PASSWORD', None)
TAX_RATE = os.getenv('TAX_RATE', None)
TOKEN_EXPIRY = os.getenv('TOKEN_EXPIRY', 10)  # Default to 1 hour if not set