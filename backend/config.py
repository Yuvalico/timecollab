import os
from dotenv import load_dotenv

load_dotenv()  
class Config:
    JWT_SECRET_KEY  = os.getenv('JWT_SECRET', 'your_jwt_secret_key')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'Name')
    DB_USER = os.getenv('DB_USER', 'User')
    DB_PASSWORD = os.getenv('DB_PASS', 'pass')

    WEB_URL = os.getenv('WEB_URL', 'localhost')
    WEB_PORT = os.getenv('WEB_PORT', '5173')