import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'pinterest-klon-secret-key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME = 60
REFRESH_TOKEN_LIFETIME = 30
