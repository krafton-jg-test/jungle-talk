from flask import request, jsonify, url_for, render_template
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from auth import auth_bp
import uuid
import os
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# client = MongoClient('mongodb://test:test@13.124.143.165', port=27017, uuidRepresentation='standard') # 실제 서버 db
client = MongoClient('mongodb://webserver:webserver@43.200.205.11',
                     port=27017, uuidRepresentation='standard')  # 실제 서버 db
db = client.testdb
user_collection = db.users

# 회원가입 API


@auth_bp.route('/signup', methods=['POST'])
def sign_up():
    try:
        user_name = request.form['name']
        login_id = request.form['login_id']
        password = request.form['password']
        print(user_name,login_id,password)
        # 유저가 넘긴 프로필 이미지 없으면 기본 이미지로 설정
        if 'profile_image' not in request.files or request.files['profile_image'].filename == '':
            profile_img_path = 'static/profile/default_profile_image.png'
            filename = "default_profile_image.png"
            print(filename)

        else:
            profile_img_file = request.files['profile_image']  # 프로필 이미지 파일
            filename = secure_filename(
                profile_img_file.filename)  # 파일명 안전하게 처리
            print(filename)
            profile_img_file.save(os.path.join('static/profile'), filename)
            print(filename)
            profile_img_path = f"profile/{filename}"

  

        new_user = {'login_id': login_id, 'password': password,
                    'profile_image': profile_img_path, 'uuid': uuid.uuid1(), 'user_name': user_name}
 
        user_collection.insert_one(new_user)
    except:
        return jsonify({'is_success': 0, 'msg': '회원가입에 실패하였습니다.'})
    return jsonify({'is_success': 1, 'msg': '회원가입에 성공하였습니다.', 'profile_img': url_for('static', filename=f"{profile_img_path}")})

# 회원가입 아이디 중복확인


@auth_bp.route('/signup/duplication-check', methods=['POST'])
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

# 로그인 페이지 렌더링
@auth_bp.route('/dashboard', methods=['GET'])
def render_logined_page():
    return render_template('index_login.html')
    
# 로그인
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # 유저의 아이디, 비밀번호 입력받음
        login_id = request.form['login_id']
        password = request.form['password']
        print(login_id,password)
        # 유저의 로그인아이디에 해당하는 비밀번호 조회
        target_pw = user_collection.find_one(
            {'login_id': login_id})['password']

        # 입력한 비밀번호 해당하는 비밀번호 같으면 토큰 발행
        if (password == target_pw):
            user_uuid = user_collection.find_one({'login_id': login_id})['uuid']
            access_token = create_access_token(identity=user_uuid)
            return jsonify({
                'is_success': 1,
                'access_token': access_token,
                'msg': '로그인에 성공하였습니다.'
                })
        else:
            return jsonify({
                'is_success': 0,
                'msg': '로그인에 실패하였습니다.1'
            })
    except:
        return jsonify({
            'is_success': 0,
            'msg': '로그인에 실패하였습니다.'
        })
        
# 토큰으로 유저 정보 받아오는 api
@auth_bp.route('/info', methods=['GET'])
@jwt_required()
def get_user_info():
    try:
        # binary 타입으로 저장된 uuid이기 때문에 UUID 객체로 변환해서 사용해야함
        current_user = get_jwt_identity()
        current_user_uuid = uuid.UUID(current_user)
        
        user_data = user_collection.find_one({'uuid': current_user_uuid})
        
        return jsonify({
            'is_success': 1,
            'user_name': user_data['user_name'],
            'profile_image': user_data['profile_image'],
            'msg': '유저 정보 불러오기를 성공하였습니다.'
        })
    except:
        return jsonify({
            'is_success': 0,
            'msg': '유저 정보 불러오기를 실패하였습니다.'
        })
