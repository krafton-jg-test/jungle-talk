from flask import request, jsonify, url_for, render_template
from pymongo import MongoClient
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from chat import chat_bp
from bson import ObjectId

import uuid

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
        uuid_list = chatroom_collection.find_one({'_id': ObjectId(chatroom_id)})['users']
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

    for uuid_data in uuid_list:
        if isinstance(uuid_data, uuid.UUID):
            pass
        else:
            uuid_data = uuid.UUID(uuid_data)
            
        user_data = user_collection.find_one({'uuid': uuid_data})
        user_dict = {
            'uuid': str(user_data['uuid']), 'user_name': user_data['user_name'], 'user_image': user_data['profile_image']}
        user_list.append(user_dict)

    return user_list

# 채팅방 페이지 렌더링
@chat_bp.route('/chatrooms/index')
def render_chatroom_page():
    return render_template('chatroom.html')

# 채팅방 입장


@chat_bp.route('/chatrooms/enter', methods=['POST'])
@jwt_required()
def enter_chatroom():
    user_uuid = get_jwt_identity()
    if (user_uuid is None):
        
        # 유효 여부에 따라 로그인 시 메인페이지 / 비로그인시 메인페이지 (render_template으로 보내기)
        return jsonify({
            'is_success': 0,
            'msg': '로그인해야 합니다.'
        })

    # 이미 채팅방에 들어와 있는 유저라면 바로 채팅방 입장
    chatroom_id = request.form['chatroom_id']
    
    user_list = chatroom_collection.find_one({'_id': ObjectId(chatroom_id)})['users']
    
    if user_uuid in user_list:
        return jsonify({
            'is_success': 1,
            'msg': '채팅방에 입장하였습니다.',
            'redirect_url': url_for('chat.render_chatroom_page', chatroom_id = chatroom_id, count = -1)
        })

    # 채팅방에 들어와 있는 유저가 아니면 비밀번호 검증
    chatroom_pw = request.form['chatroom_pw']

    chatroom_password = chatroom_collection.find_one(
        {'_id': ObjectId(chatroom_id)}, {'chatroom_password': 1})['chatroom_password']
    if (chatroom_pw != chatroom_password):
        return jsonify({
            'is_success': 0,
            'msg': '채팅방 입장에 실패했습니다.'
        })

    chatroom_collection.update_one(
        {'_id': ObjectId(chatroom_id)}, {'$push': {'users': user_uuid}})
    
    return jsonify({
            'is_success': 1,
            'msg': '채팅방에 입장하였습니다.',
            'redirect_url': url_for('chat.render_chatroom_page', chatroom_id = chatroom_id, count = -1)
        })

# 모든 채팅방 정보 불러오기(메인페이지)


@chat_bp.route('/chatrooms', methods=['GET'])
def get_all_chatroom():
    try:
        # mongoDB의 aggregation pipeline 사용해서 데이터 한번에 처리
        pipeline = [
            {
                '$project': {
                    'chatroom_id': 1,
                    'chatroom_name': 1,
                    'description': 1,
                    'count': {'$size': '$users'}
                }
            }
        ]
        chatroom_data = list(chatroom_collection.aggregate(pipeline))
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
        client_msg_count = int(request.args.get('count'))  # 클라이언트의 메시지 카운트
        server_msg_count = chatroom_collection.find_one({'_id': ObjectId(chatroom_id)})['message_count']  # 서버의 메시지 카운트

        # 유저가 처음 입장하면 채팅방의 메시지 갯수 -1, 서버의 메시지 갯수를 count로 지정
        if (client_msg_count == -1):
            count = server_msg_count

        elif (server_msg_count >= client_msg_count):
            count = server_msg_count - client_msg_count

        elif (server_msg_count < client_msg_count):
            count = 100 + client_msg_count - server_msg_count
            
        message_list = list(message_collection.find({'chatroom_id': chatroom_id}, {
                                               'uuid': 1, 'message_content': 1, 'message_time': 1, '_id': False}).limit(count).sort('message_time'))
        
        for msg in message_list:
            if 'message_time' in msg and isinstance(msg['message_time'], datetime):
                msg['message_time'] = msg['message_time'].strftime('%Y년 %m월 %d일 %H:%M')
        
        # # aggregation pipeline
        # pipeline = [
        #     {'$match': {'chatroom_id': chatroom_id}},
        #     {'$sort': {'message_time': -1}},
        #     {'$limit': count},
        #     {'$project': {
        #         '_id': False,
        #         'uuid': True,
        #         'message': True,
        #         'message_time': True
        #         # 'message_time': {'$dateToString': {'format': '%Y-%m-%dT%H:%M', 'date': '$message_time'}}
        #     }}
        # ]
        # message_list = list(message_collection.aggregate(pipeline))
    except:
        return jsonify({
            'is_success': 0,
            'count': server_msg_count,
            'msg': '채팅기록 불러오기에 실패하였습니다.'
        })
    return jsonify({
        'list': message_list,
        'count': count,
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

        pure_message_time = datetime.now()
        message_time = pure_message_time.isoformat()

        # 메시지 수 증가 처리 및 마지막 채팅 시간 수정
        chatroom_collection.update_one(
            {'_id': ObjectId(chatroom_id)},
            {'$inc': {'message_count': 1}, '$set': {'last_chat_time': pure_message_time}}
        )

        message_data = {
            'chatroom_id': chatroom_id,
            'message_content': message,
            'message_time': pure_message_time,
            'uuid': user_uuid
        }
        message_collection.insert_one(message_data)
    except:
        return jsonify({
            'is_success': 0,
            'msg': '채팅입력에 실패하였습니다.'
        })

    return jsonify({
        'chatroom_id': chatroom_id,
        'message_time': message_time,
        'is_success': 1,
        'msg': '채팅 입력에 성공하였습니다.'
    })

# 채팅방 생성


@chat_bp.route('/chatrooms', methods=['POST'])
@jwt_required()
def create_chatroom():
    user_uuid = get_jwt_identity()
    if user_uuid is None:
        return jsonify({
            'is_success': 0,
            'msg': '로그인해야 합니다.'
        })
        
    try:
        chatroom_name = request.form['chatroom_name']
        chatroom_pw = request.form['chatroom_pw']
        description = request.form['description']

        last_chat_time = datetime.now()

        chatroom_data = {
            'chatroom_name': chatroom_name,
            'chatroom_password': chatroom_pw,
            'description': description,
            'users': [user_uuid],
            'uuid': user_uuid,
            'message_count': 0,
            "last_chat_time": last_chat_time  # TTL 지나면 삭제되도록 설정된 컬럼
        }
        result_data = chatroom_collection.insert_one(chatroom_data)
        chatroom_id = result_data.inserted_id

    except:
        return jsonify({
            'is_success': 0,
            'msg': '채팅방 생성에 실패하였습니다.'
        })

    return jsonify({
        'is_success': 1,
        'msg': '채팅방 생성에 성공하였습니다.',
        'chatroom_id': chatroom_id
    })
