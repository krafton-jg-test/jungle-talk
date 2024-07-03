from flask import Flask, render_template, request, jsonify, url_for ,redirect
from bson import ObjectId
from pymongo import MongoClient
from flask.json.provider import JSONProvider
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from werkzeug.utils import secure_filename
from auth.routes import auth_bp
from chat.routes import chat_bp
from config.settings import JWT_config

import json


def start_app():
    # Flask 애플리케이션 인스턴스 생성
    app = Flask(__name__, instance_relative_config=True)

    jwt = JWTManager(app)  # app에 JWT 확장 모듈 등록

    # jwt 관련 설정 추가
    app.config.from_object(JWT_config)

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

# <<<<<<< server
    # TTL 설정. 채팅방이 마지막 채팅이 올라온지 7일이 지나면 자동으로 삭제되도록 설정(last_chat_time에 설정)
    # client = MongoClient('mongodb://test:test@13.124.143.165', port=27017, uuidRepresentation='standard') # 실제 서버 db
    client = MongoClient('mongodb://webserver:webserver@43.200.205.11',
                         port=27017, uuidRepresentation='standard')
    db = client.testdb
    chatroom_collection = db.chatrooms
    chatroom_collection.create_index("last_chat_time", expireAfterSeconds=80)

    # 블루프린트 등록
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')

    app.config.update(
        DEBUG=True,
        JWT_SECRET_KEY="TEST"  # JWT 시크릿 키 설정
    )

    app.config['JWT_ACCESS_TOKEN_EXPIRATION'] = timedelta(
        hours=5)  # 액세스토큰 만료시간 1시간으로 설정

    return app


if __name__ == '__main__':
    app = start_app()
    app.run('0.0.0.0', port=5000, debug=True)


@app.route('/')
def home():
    return 'This is Home!'

# # 회원가입 API
# @app.route('/signup', methods=['POST'])
# def sign_up():
#     # try:
#     user_name = request.form['name']

#     # 유저가 넘긴 프로필 이미지 없으면 기본 이미지로 설정
#     if 'profile_image' not in request.files or request.files['profile_image'].filename == '':
#         profile_img_path = 'static/profile/default_profile_image.png'
#         filename = "default_profile_image.png"

#     else:
#         profile_img_file = request.files['profile_image']  # 프로필 이미지 파일
#         filename = secure_filename(profile_img_file.filename)  # 파일명 안전하게 처리
#         app.config['UPLOAD_FOLDER'] = 'static/profile'
#         profile_img_file.save(os.path.join(
#             app.config['UPLOAD_FOLDER'], filename))
#         profile_img_path = f"profile/{filename}"

#     login_id = request.form['login_id']
#     password = request.form['password']

#     new_user = {'login_id': login_id, 'password': password,
#                 'profile_image': profile_img_path, 'uuid': uuid.uuid1(), 'user_name': user_name}

#     user_collection.insert_one(new_user)
#     # except:
#     #     return jsonify({'is_success': 0, 'msg': '회원가입에 실패하였습니다.'})
#     return jsonify({'is_success': 1, 'msg': '회원가입에 성공하였습니다.', 'profile_img': url_for('static', filename=f"{profile_img_path}")})

# # 회원가입 아이디 중복확인 API
# @app.route('/signup/duplcation-check', methods=['POST'])
# def check_username_duplication():
#     login_id = request.form['id']
#     if (user_collection.find_one({'login_id': login_id})):
#         return jsonify(
#             {
#                 'is_duplicate': 1,
#                 'msg': '이미 존재하는 아이디입니다.'
#             }
#         )
#     return jsonify(
#         {
#             'is_duplicate': 0,
#             'msg': '중복되는 아이디가 없습니다.'
#         }
#     )

# # 로그인 API(여기서 토큰 사용해서 확인)
# @app.route('/login', methods=['POST'])
# def login():
#     try:
#         # 유저의 아이디, 비밀번호 입력받음
#         login_id = request.form['login_id']
#         password = request.form['password']

#         # 유저의 로그인아이디에 해당하는 비밀번호 조회
#         target_pw = user_collection.find_one(
#             {'login_id': login_id})['password']

#         # 입력한 비밀번호 해당하는 비밀번호 같으면 토큰 발행
#         if (password == target_pw):
#             access_token = create_access_token(identity=login_id)
#             return jsonify({'access_token': access_token})
#         else:
#             return jsonify({
#                 'is_success': 0,
#                 'msg': '로그인에 실패하였습니다.'
#             })
#     except:
#         return jsonify({
#             'is_success': 0,
#             'msg': '로그인에 실패하였습니다.'
#         })

# # 모든 채팅방 정보 불러오기 API(메인페이지)
# @app.route('/chatrooms', methods=['GET'])
# def get_all_chatroom():
#     try:
#         chatroom_data = list(chatroom_collection.find(
#             {}, {'chatroom_id': 1, 'chatroom_name': 1, 'description': 1}))  # find all
#         # return render_template('index.html', )
#         return jsonify({
#             'list': chatroom_data,
#             'is_success': 1,
#             'msg': '채팅방 정보 반환에 성공하였습니다.'
#         })
#     except:
#         return jsonify({
#             'is_success': 0,
#             'msg': '채팅방 정보 반환에 실패하였습니다.'
#         })

# # 채팅방에 참여중인 유저 리스트 반환 API


# @app.route('/chatrooms/users', methods=['GET'])
# def get_chatroom_users():
#     try:
#         chatroom_id = request.args.get('chatroom_id')
#         uuid_list = list(chatroom_collection.find_one(
#             {'_id': chatroom_id})['users'])
#         user_list = get_users(uuid_list)
#     except:
#         return jsonify({
#             'is_success': 0,
#             'msg': '유저들 정보 반환에 실패하였습니다.'
#         })
#     return jsonify({
#         'list': user_list,
#         'is_success': 1,
#         'msg': '유저들 정보 반환에 성공하였습니다.'
#     })

# # 유저 정보 반환하는 내부 함수


# def get_users(uuid_list):

#     user_list = []

#     for uuid in uuid_list:
#         user_data = user_collection.find_one({'uuid': uuid})
#         user_dict = {
#             'uuid': uuid, 'user_name': user_data['user_name'], 'user_image': user_data['profile_image']}
#         user_list.append(user_dict)

#     return user_list

# 채팅방 입장하기 API
# <<<<<<< server


# @app.route('/chatrooms/enter', methods=['POST'])
# @jwt_required()
# def enter_chatroom():
#     current_user = get_jwt_identity()
#     if (current_user is None):
#         return jsonify({
#             'is_success': 0,
#             'msg': '로그인해야 합니다.'
#         })

#     chatroom_id = request.form['chatroom_id']
#     chatroom_pw = request.form['chatroom_pw']
#     user_uuid = request.form['uuid']

#     chatroom_password = chatroom_collection.find_one(
#         {'_id': chatroom_id}, {'chatroom_password': 1})
#     if (chatroom_pw != chatroom_password):
#         return jsonify({
#             'is_success': 0,
#             'msg': '채팅방 입장에 실패했습니다.'
#         })

#     chatroom_collection.update_one(
#         {'_id': chatroom_id}, {'$push': {'users': user_uuid}})
#     # return render_template('chatroom.html', chatroom_id = chatroom_id)
#     return url_for('chatroom', chatroom_id=chatroom_id)

# # 특정 채팅방의 채팅기록 불러오기 API
# @app.route('/chatrooms/messages', methods=['GET'])
# def get_chatroom():
#     try:
#         chatroom_id = request.args.get('chatroom_id')
#         client_msg_count = request.args.get('count')  # 클라이언트의 메시지 카운트
#         server_msg_count = chatroom_collection.find_one(
#             'chatroom_id')['message_count']  # 서버의 메시지 카운트

#         if (client_msg_count == -1):
#             count = server_msg_count

#         elif (server_msg_count >= client_msg_count):
#             count = server_msg_count - client_msg_count

#         elif (server_msg_count < client_msg_count):
#             count = 100 + client_msg_count - server_msg_count

#         message_list = message_collection.find({'_id': chatroom_id}, {
#                                                'uuid': 1, 'message': 1, 'message_time': 1, '_id': False}).limit(count).sort('message_time')
#     except:
#         return jsonify({
#             'is_success': 0,
#             'count': server_msg_count,
#             'msg': '채팅기록 불러오기에 실패하였습니다.'
#         })
#     return jsonify({
#         'list': message_list,
#         'count': server_msg_count,
#         'is_success': 1,
#         'msg': '채팅기록 불러오기에 성공하였습니다.'
#     })

# # 채팅 입력 API
# @app.route('/chatrooms/messages', methods=['POST'])
# def send_message():
#     try:
#         chatroom_id = request.form['chatroom_id']
#         user_uuid = request.form['uuid']
#         message = request.form['message']

#         message_time = datetime.now()

#         # 메시지 수 증가 처리 및 마지막 채팅 시간 수정
#         chatroom_collection.update_one(
#             {'_id': chatroom_id},
#             {'$inc': {'message_count': 1}, '$set': {'last_chat_time': message_time}}
#         )

#         message_data = {
#             'chatroom_id': chatroom_id,
#             'message_content': message,
#             'message_time': message_time,
#             'uuid': user_uuid
#         }
#         message_collection.insert_one(message_data)
#     except:
#         return jsonify({
#             'is_success': 0,
#             'msg': '채팅입력에 실패하였습니다.'
#         })

#     return jsonify({
#         'message_time': message_time,
#         'is_success': 1,
#         'msg': '채팅 입력에 성공하였습니다.'
#     })

# # 채팅방 생성 API
# @app.route('/chatrooms', methods=['POST'])
# def create_chatroom():
#     try:
#         chatroom_name = request.form['chatroom_name']
#         chatroom_pw = request.form['chatroom_pw']
#         description = request.form['description']
#         creator_uuid = request.form['uuid']

#         last_chat_time = datetime.now()

#         chatroom_data = {
#             'chatroom_name': chatroom_name,
#             'chatroom_password': chatroom_pw,
#             'description': description,
#             'users': [creator_uuid],
#             'uuid': creator_uuid,
#             'message_count': 0,
#             "last_chat_time": last_chat_time  # TTL 지나면 삭제되도록 설정된 컬럼
#         }
#         chatroom_collection.insert_one(chatroom_data)

#     except:
#         return jsonify({
#             'is_success': 0,
#             'msg': '채팅방 생성에 실패하였습니다.'
#         })

#     return jsonify({
#         'is_success': 1,
#         'msg': '채팅방 생성에 성공하였습니다.'
#     })
