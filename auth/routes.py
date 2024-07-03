from flask import request, jsonify, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import uuid, os
from flask_jwt_extended import create_access_token
from . import auth_bp

# client = MongoClient('mongodb://test:test@13.124.143.165', port=27017, uuidRepresentation='standard') # 실제 서버 db
client = MongoClient('mongodb://webserver:webserver@43.200.205.11',
                     port=27017, uuidRepresentation='standard')
db = client.testdb
user_collection = db.users

# 회원가입 API
@auth_bp.route('/signup', methods=['POST'])
def sign_up():
    try:
        user_name = request.form['name']

        # 유저가 넘긴 프로필 이미지 없으면 기본 이미지로 설정
        if 'profile_image' not in request.files or request.files['profile_image'].filename == '':
            profile_img_path = 'static/profile/default_profile_image.png'
            filename = "default_profile_image.png"

        else:
            profile_img_file = request.files['profile_image']  # 프로필 이미지 파일
            filename = secure_filename(
                profile_img_file.filename)  # 파일명 안전하게 처리
            profile_img_file.save(os.path.join('static/profile'), filename)
            profile_img_path = f"profile/{filename}"

        login_id = request.form['login_id']
        password = request.form['password']

        new_user = {'login_id': login_id, 'password': password,
                    'profile_image': profile_img_path, 'uuid': uuid.uuid1(), 'user_name': user_name}

        user_collection.insert_one(new_user)
    except:
        return jsonify({'is_success': 0, 'msg': '회원가입에 실패하였습니다.'})
    return jsonify({'is_success': 1, 'msg': '회원가입에 성공하였습니다.', 'profile_img': url_for('static', filename=f"{profile_img_path}")})

# 회원가입 아이디 중복확인


@auth_bp('/signup/duplication-check', methods=['POST'])
def check_username_duplication():
    login_id = request.form['id']
    if (user_collection.find_one({'login_id': login_id})):
        return jsonify(
            {
                'is_duplicate': 1,
                'msg': '이미 존재하는 아이디입니다.'
            }
        )
    return jsonify(
        {
            'is_duplicate': 0,
            'msg': '중복되는 아이디가 없습니다.'
        }
    )

# 로그인


@auth_bp('/login', methods=['POST'])
def login():
    try:
        # 유저의 아이디, 비밀번호 입력받음
        login_id = request.form['login_id']
        password = request.form['password']

        # 유저의 로그인아이디에 해당하는 비밀번호 조회
        target_pw = user_collection.find_one(
            {'login_id': login_id})['password']

        # 입력한 비밀번호 해당하는 비밀번호 같으면 토큰 발행
        if (password == target_pw):
            access_token = create_access_token(identity=login_id)
            return jsonify({'access_token': access_token})
        else:
            return jsonify({
                'is_success': 0,
                'msg': '로그인에 실패하였습니다.'
            })
    except:
        return jsonify({
            'is_success': 0,
            'msg': '로그인에 실패하였습니다.'
        })
