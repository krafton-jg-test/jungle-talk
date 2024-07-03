let idCheck = 0;

$(document).ready(function () {
    //채팅방 로딩 
    loadChatRoomList()

    //채팅방 입장하기 패스워드 모달 //
    $('#passwdform').on('submit',function(event){
        event.preventDefault();
        enterChatRoom()
    })
    //로그인 모달 
    $('#loginform').on('submit',function(event){
        event.preventDefault();
        loginRequest(this)
    })

    //회원가입 모달
    $('#signupform').on('submit',function(event){
        event.preventDefault();
        register()
    })
    //중복검사
    $('#duplicate').on('click',function(){
        doIdCheck()
    })
});

function loginRequest(element){
    const formData = $(element).serialize();
    $.ajax({
        url: '/auth/login', // 서버의 엔드포인트 URL
        type: 'POST', // HTTP 요청 메서드 (GET, POST 등)
        data: formData, // 전송할 데이터
        success: function(response) {
          if(response['is_success']==1){
            localStorage.setItem('access_token',response['access_token'])
            window.location.href='/dashboard'
          }
        },
        error: function(error) {
          console.error('Login Error:', error);
          // 로그인 에러 시 처리할 코드
        }
      });
}

function register(){
    if(idCheck == 0){
        alert("중복체크를 해주세요!!")
        return
    }
    let input_id = $("#signup-id").val()
    let input_passwd=$("#signup-passwd").val()
    let input_name=$('#signup-name').val()
    let input_image=$('#signup-image').val()
    
    if(input_id == undefined){
        alert("아이디를 입력해 주세요!!")
        return   
    }else if( input_passwd == undefined){
        alert("비밀번호를 입력해 주세요!!")
        return
    }else if( input_name == undefined){
        alert("이름을 입력해 주세요!!")
        return
    }
    let post_data ={
        'id':input_id,
        'passwd':input_passwd,
        'name':input_name,
        'image':input_image,
    }
}

//중복체크 
function doIdCheck(){
    if(idCheck==1){
        alert("사용 가능한 아이디 입니다!!")
        return
    }
    let input_id = $("#signup-id").val()
    $.ajax({
        type:"POST",
        url:'/signup/duplicate-check',
        data:{
            'id':input_id
        },
        success: function(response){
            if(response['is_duplicate']==1){
                idCheck=1;
                doIdCheck();
            }
        }
    })
}
//채팅방 입장 
function enterChatRoom(){
    let room_id = $('#passwd').find('#hidden-data').val()
    let room_pw = $('#passwd').find('#input-pw').val()

    $.ajax({
        type: "POST",
        url: '/chat/chatrooms/enter',
        headers:{
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        data: {
            'chatroom_id': room_id,
            'chatroom_pw': room_pw,
        },
        success: function (response) {
            if(response['is_success']==1)
                window.location.href = response['url']
            else{
                alert('로그인을 해주세요!!')
            }
        }
    })
}

//채팅방 목록 불러오기 
function loadChatRoomList() {
    console.log('test')
    $.ajax({
        type: 'GET',
        url: '/chat/chatrooms',
        data: {},
        success: function (response) {
            if (response['is_success'] == 1) {
                for (let item in response['list']) {
                    makeChatRoom(
                        item['chatroom_id'],
                        item['chatroom_name'],
                        item['description'],
                        item['count']
                    )
                }
            }
        }
    })
}
//채팅방 낱개 추가 
function makeChatRoom(chatroom_id, chatroom_name, description, count) {
    tempbox =
        `<div onclick="passwd.showModal()" class="chatroom-box flex justify-center items-center flex-col border-opacity-50 my-6">
            <input class="chatroom-id" type="hidden" value="${chatroom_id}">
            <div class="w-1/2 overflow-hidden rounded-lg ring-1 ring-gray-200">
                <div class="flex items-center justify-between pl-4 bg-gray-100 border-b border-gray-200">
                    <h2 class="chatroom-name text-lg font-semibold text-gray-800">${chatroom_name}</h2>
                </div>
                <div class="chatroom-description p-4 bg-[#1F978B]">
                    <h3 class="chatroom-description pl-0 text-[#FEFEFE]">${description}</h3>
                </div>
            </div>
    </div>`
    $('#chatroom-box').append(tempbox)
}
