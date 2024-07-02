from flask import Flask, render_template, request, jsonify
from bson import ObjectId
from pymongo import MongoClient
from flask.json.provider import JSONProvider

import json, sys

# client = MongoClient('mongodb://test:test@localhost', 27017) # 실제 서버 db
client = MongoClient('localhost', 27017) # 로컬 db
db = client.testdb

user_table = db.users
chatroom_table = db.chatrooms
message_table = db.messages

app = Flask(__name__)

#test
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

# 위에 정의된 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)

@app.route('/')
def home():
   return 'This is Home!'

# 회원가입 API
@app.route('/signup', methods=['POST'])
def sign_up():
    
    return

# 회원가입 아이디 중복확인 API
@app.route('/signup/duplcation-check', methods=['GET'])
def check_username_duplication():
    return

# 로그인 API
@app.route('/login', methods=['GET'])
def login():
    return

# 모든 채팅방 정보 반환 API
@app.route('/chatrooms/all', methods=['GET'])
def get_all_chatroom():
    return

# 채팅방 입장 여부 확인 API
@app.route('/chatrooms/invited', methods=['GET'])
def get_chat():
    return

# 채팅방 입장하기 API
@app.route('/chatrooms/enter', methods=['POST'])
def enter_chatroom():
    return

# 특정 채팅방의 채팅기록 불러오기 API
@app.route('/chatrooms', methods=['GET'])
def get_chatroom():
    return

# 5초 단위 해당 채팅방의 채팅 갯수 값 불러오기 API
@app.route('/chatrooms/message-counts', methods=['GET'])
def count_message():
    return

# # 채팅방 새로고침 API
# @app.route('/chatrooms/refresh', methods=['GET'])
# def refresh_chatroom():
#     return

# 채팅 입력 API
@app.route('/chatrooms/write', methods=['POST'])
def send_message():
    return

# 채팅방 생성 API
@app.route('/chatrooms/create', methods=['POST'])
def create_chatroom():
    return

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)