import os

BASE_DIR = os.getenv("BASE_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORS_WHITE = os.getenv("CORS_WHITELIST", 'http://10.168.2.108:9527')
DB_NAME = os.getenv("DB_NAME", "wg_online")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
API_HOST = os.getenv("API_HOST", "10.168.2.111")  # PC端地址
API_PORT = os.getenv("API_PORT", "8000")  # PC端接口
ADMIN_API_HOST = os.getenv("ADMIN_API_HOST", "10.168.2.107")  # 后台地址
ADMIN_API_PORT = os.getenv("ADMIN_API_PORT", "9526")  # 后台端口
