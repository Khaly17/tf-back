import os

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
    JWT_SECRET_KEY = "super-secret-key" 
    JWT_ALGORITHM = "HS256"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'db-password')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'tfdb')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

    JWT_ACCESS_TOKEN_EXPIRES = 900        
    JWT_REFRESH_TOKEN_EXPIRES = 86400 

    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}'
        f'@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    )

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'diengkhaly17@gmail.com'
    MAIL_PASSWORD = 'abyw ibhi psox cect'  
    MAIL_DEFAULT_SENDER = 'diengkhaly17@gmail.com'
