from flask import Flask
from bson import ObjectId
from pymongo import MongoClient
from flask.json.provider import JSONProvider
from flask_jwt_extended import JWTManager
from auth.routes import auth_bp
from chat.routes import chat_bp
from config.settings import JWT_config

import json

app = Flask(__name__, instance_relative_config=True)

def start_app():
    # Flask 애플리케이션 인스턴스 생성
    app = Flask(__name__, instance_relative_config=True)

    # jwt 관련 설정 추가
    app.config.from_object(JWT_config)
    app.config['JWT_SECRET_KEY'] = 'TEST'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=5)
    jwt = JWTManager(app)  # app에 JWT 확장 모듈 등록
    
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return json.JSONEncoder.default(self, o)

    class CustomJSONProvider(JSONProvider):
        def dumps(self, obj, **kwargs):
            return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

        def loads(self, s, **kwargs):
            return json.loads(s, **kwargs)

    # 위에 정의된 custom encoder를 사용하도록 설정한다.
    app.json = CustomJSONProvider(app)

    # TTL 설정. 채팅방이 마지막 채팅이 올라온지 7일이 지나면 자동으로 삭제되도록 설정(last_chat_time에 설정)
    # client = MongoClient('mongodb://test:test@13.124.143.165', port=27017, uuidRepresentation='standard') # 실제 서버 db
    client = MongoClient('mongodb://webserver:webserver@43.200.205.11',
                         port=27017, uuidRepresentation='standard')
    db = client.testdb
    chatroom_collection = db.chatrooms
    chatroom_collection.create_index("last_chat_time", expireAfterSeconds=80) # 임의로 80초로 설정

    # 블루프린트 등록
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')

    app.config['JWT_ACCESS_TOKEN_EXPIRATION'] = timedelta(
        hours=5)  # 액세스토큰 만료시간 5시간으로 설정
    @app.route('/')
    def home():
        return render_template('index.html')

    return app


if __name__ == '__main__':
    app = start_app()
    app.run('0.0.0.0', port=5000, debug=True)