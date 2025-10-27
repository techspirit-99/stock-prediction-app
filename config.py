import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///stock_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ['headers']
