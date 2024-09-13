import os

class Config:
    SECRET_KEY = os.getenv('JWT_SECRET', 'your_jwt_secret_key')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'Name')
    DB_USER = os.getenv('DB_USER', 'User')
    DB_PASSWORD = os.getenv('DB_PASS', 'pass')
    # DB_HOST = 'localhost'
    # DB_NAME = 'tlv300'
    # DB_USER = 'postgres'
    # DB_PASSWORD = 'kokonoko'