from datetime import timedelta

class JWT_config:
    DEBUG = True
    JWT_SECRET_KEY = "TEST"
    JWT_ACCESS_TOKEN_EXPIRATION = timedelta(hours = 5) # 액세스 토큰 만료시간 5시간으로 설정