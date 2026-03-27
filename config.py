import os
from dotenv import load_dotenv

# 锁定项目根目录，确保路径在 Docker 容器内不偏移
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# 精准加载 instance 目录下的 .env
load_dotenv(os.path.join(BASE_DIR, 'instance', '.env'))

class Config:
    BASE_DIR = BASE_DIR

    ADMIN_KEY = os.environ.get('ADMIN_KEY')
    if not ADMIN_KEY:
        raise ValueError("CAN NOT FIND ADMIN_KEY！")

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("CAN NOT FIND SECRET_KEY！")

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'clinic.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')