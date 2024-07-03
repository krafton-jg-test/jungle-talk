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
        register(this)
    })
    //중복검사
    $('#duplicate').on('click',function(){
        doIdCheck()
    })
});
//로그인
function loginRequest(element){
    const formData = $(element).serialize();
    $.ajax({
        url: '/auth/login', // 서버의 엔드포인트 URL
        type: 'POST', // HTTP 요청 메서드 (GET, POST 등)
        data: formData, // 전송할 데이터
        success: function(response) {
          if(response['is_success']==1){
            localStorage.setItem('access_token',response['access_token'])
            window.location.href='/auth/dashboard'
          }
        },
        error: function(error) {
          console.error('Login Error:', error);
          // 로그인 에러 시 처리할 코드
        }
      });
}
//회원가입 
function register(element){
    console.log('register')

    const formData = new FormData();
    console.log($('#sign-id').val(),
    $('#sign-password').val(),
    $('#sign-name').val(),
    $('#sign-image')[0].files[0])
    formData.append('login_id', $('#sign-id').val());
    formData.append('password', $('#sign-password').val());
    formData.append('name', $('#sign-name').val());
    formData.append('profile_image', $('#sign-image')[0].files[0]); // 파일을 FormData에 추가
    console.log(formData)
    // $.ajax({
    //     type:"POST",
    //     url:'/auth/signup',
    //     data:formData,
    //     contentType: false,
    //     processData: false, 
    //     success:function(response){
    //             console.log(posted)
    //             alert(response['msg'])
    //     }
    // })
    $.ajax({
        url:'/auth/signup', // 업로드할 서버의 엔드포인트 URL
        type: 'POST', // HTTP 요청 메서드 (GET, POST 등)
        data: formData, // 전송할 데이터 (FormData 객체)
        contentType: false, // 데이터 타입 (파일 업로드 시 false로 설정)
        processData: false, // 데이터 처리 방식 (FormData 객체 사용 시 false로 설정)
        success: function(response) {
            if(response['is_success']==1){
                alert( response['msg']);
               
            }else{
                alert(response['msg'])
            }
            window.location.reload()
        },
        error: function(error) {
          console.error('Upload Error:', error);
          // 업로드 에러 시 처리할 코드
        }
      });
}

//중복체크 
function doIdCheck(){
    let input_id = $("#signup-id").val()
    $.ajax({
        type:"POST",
        url:'/auth/signup/duplication-check',
        data:{
            'id':input_id
        },
        success: function(response){
            if(response['is_duplicate']==1){
                alert("사용 가능한 아이디 입니다!!")
            }else
                alert("이미 사용중인 아이디 입니다.")
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
