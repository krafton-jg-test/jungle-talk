from flask import request, jsonify, url_for
from pymongo import MongoClient
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from chat import chat_bp

# client = MongoClient('mongodb://test:test@13.124.143.165', port=27017, uuidRepresentation='standard') # 실제 서버 db
client = MongoClient('mongodb://webserver:webserver@43.200.205.11',
                     port=27017, uuidRepresentation='standard')  # 실제 서버 db

db = client.testdb
chatroom_collection = db.chatrooms
user_collection = db.users
message_collection = db.messages

# 채팅방에 참여중인 유저 리스트 반환


@chat_bp.route('/chatrooms/users', methods=['GET'])
def get_chatroom_users():
    try:
        chatroom_id = request.args.get('chatroom_id')
        uuid_list = list(chatroom_collection.find_one(
            {'_id': chatroom_id})['users'])
        user_list = get_users(uuid_list)
    except:
        return jsonify({
            'is_success': 0,
            'msg': '유저들 정보 반환에 실패하였습니다.'
        })
    return jsonify({
        'list': user_list,
        'is_success': 1,
        'msg': '유저들 정보 반환에 성공하였습니다.'
    })

# get_chatroom_users()의 유저 정보 반환용 내부 함수


def get_users(uuid_list):

    user_list = []

    for uuid in uuid_list:
        user_data = user_collection.find_one({'uuid': uuid})
        user_dict = {
            'uuid': uuid, 'user_name': user_data['user_name'], 'user_image': user_data['profile_image']}
        user_list.append(user_dict)

    return user_list

# 채팅방 입장


@chat_bp.route('/chatrooms/enter', methods=['POST'])
@jwt_required()
def enter_chatroom():
    current_user = get_jwt_identity()
    if (current_user is None):
        return jsonify({
            'is_success': 0,
            'msg': '로그인해야 합니다.'
        })

    chatroom_id = request.form['chatroom_id']
    chatroom_pw = request.form['chatroom_pw']
    user_uuid = request.form['uuid']

    chatroom_password = chatroom_collection.find_one(
        {'_id': chatroom_id}, {'chatroom_password': 1})
    if (chatroom_pw != chatroom_password):
        return jsonify({
            'is_success': 0,
            'msg': '채팅방 입장에 실패했습니다.'
        })

    chatroom_collection.update_one(
        {'_id': chatroom_id}, {'$push': {'users': user_uuid}})
    # return render_template('chatroom.html', chatroom_id = chatroom_id)
    return url_for('chatroom', chatroom_id=chatroom_id)

# 모든 채팅방 정보 불러오기(메인페이지)


@chat_bp.route('/chatrooms', methods=['GET'])
def get_all_chatroom():
    try:
        chatroom_data = list(chatroom_collection.find(
            {}, {'chatroom_id': 1, 'chatroom_name': 1, 'description': 1}))  # find all
        # return render_template('index.html', )
        return jsonify({
            'list': chatroom_data,
            'is_success': 1,
            'msg': '채팅방 정보 반환에 성공하였습니다.'
        })
    except:
        return jsonify({
            'is_success': 0,
            'msg': '채팅방 정보 반환에 실패하였습니다.'
        })

# 특정 채팅방의 채팅기록 불러오기


@chat_bp.route('/chatrooms/messages', methods=['GET'])
def get_chatroom():
    try:
        chatroom_id = request.args.get('chatroom_id')
        client_msg_count = request.args.get('count')  # 클라이언트의 메시지 카운트
        server_msg_count = chatroom_collection.find_one(
            'chatroom_id')['message_count']  # 서버의 메시지 카운트

        if (client_msg_count == -1):
            count = server_msg_count

        elif (server_msg_count >= client_msg_count):
            count = server_msg_count - client_msg_count

        elif (server_msg_count < client_msg_count):
            count = 100 + client_msg_count - server_msg_count

        message_list = message_collection.find({'_id': chatroom_id}, {
                                               'uuid': 1, 'message': 1, 'message_time': 1, '_id': False}).limit(count).sort('message_time')
    except:
        return jsonify({
            'is_success': 0,
            'count': server_msg_count,
            'msg': '채팅기록 불러오기에 실패하였습니다.'
        })
    return jsonify({
        'list': message_list,
        'count': server_msg_count,
        'is_success': 1,
        'msg': '채팅기록 불러오기에 성공하였습니다.'
    })

# 채팅 입력


@chat_bp.route('/chatrooms/messages', methods=['POST'])
def send_message():
    try:
        chatroom_id = request.form['chatroom_id']
        user_uuid = request.form['uuid']
        message = request.form['message']

        message_time = datetime.now()

        # 메시지 수 증가 처리 및 마지막 채팅 시간 수정
        chatroom_collection.update_one(
            {'_id': chatroom_id},
            {'$inc': {'message_count': 1}, '$set': {'last_chat_time': message_time}}
        )

        message_data = {
            'chatroom_id': chatroom_id,
            'message_content': message,
            'message_time': message_time,
            'uuid': user_uuid
        }
        message_collection.insert_one(message_data)
    except:
        return jsonify({
            'is_success': 0,
            'msg': '채팅입력에 실패하였습니다.'
        })

    return jsonify({
        'message_time': message_time,
        'is_success': 1,
        'msg': '채팅 입력에 성공하였습니다.'
    })

# 채팅방 생성


@chat_bp.route('/chatrooms', methods=['POST'])
def create_chatroom():
    try:
        chatroom_name = request.form['chatroom_name']
        chatroom_pw = request.form['chatroom_pw']
        description = request.form['description']
        creator_uuid = request.form['uuid']

        last_chat_time = datetime.now()

        chatroom_data = {
            'chatroom_name': chatroom_name,
            'chatroom_password': chatroom_pw,
            'description': description,
            'users': [creator_uuid],
            'uuid': creator_uuid,
            'message_count': 0,
            "last_chat_time": last_chat_time  # TTL 지나면 삭제되도록 설정된 컬럼
        }
        chatroom_collection.insert_one(chatroom_data)

    except:
        return jsonify({
            'is_success': 0,
            'msg': '채팅방 생성에 실패하였습니다.'
        })

    return jsonify({
        'is_success': 1,
        'msg': '채팅방 생성에 성공하였습니다.'
    })
