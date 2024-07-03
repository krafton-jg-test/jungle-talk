$(document).ready(function () {
    loadChatRoomList()
    // 채팅방 생성하기 모달
    $('#newchatform').on('submit', function (event) {
        event.preventDefault();
        onCreateChatroom(this)
    })
    //채팅방 입장하기 패스워드 모달 //
    $('#passwdform').on('submit', function (event) {
        event.preventDefault();
        enterChatRoom()
        console.log('here1')
    })
    //로그아웃 
    $('#logout').on('click',function(){
        localStorage.removeItem('access_token');
        window.location.href="/"
    })
});

//채팅방 생성 
function onCreateChatroom(element) {
    console.log('onCreateChatroom')
    const formData = $(element).serialize();
    $.ajax({
        type: "POST",
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        url: "/chat/chatrooms",
        data: formData,
        success: function (response) {
            let redirectionUrl = undefined;
            if (response['is_success'] == 1) {
                alert(response['msg'])
                redirectionUrl = `/chat/chatrooms/index?chatroomId=${response['chatroom_id']}`
            }
            else {
                alert(response['msg'])
                redirectionUrl = "/auth/dashboard"
            }
            window.location.href = redirectionUrl
        }
    })
}
//채팅방 입장 
function enterChatRoom(){
    let room_id = $('#passwd').find('#hidden-data').val()
    let room_pw = $('#passwd').find('#input-pw').val()
    console.log(room_id,room_pw)
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
                window.location.href = response['redirect_url']
                //console.log(response['redirect_url'])
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
                console.log(response['list'])
                for (let item of response['list']) {
                    makeChatRoom(
                        item['_id'],
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
        `<div onclick="pwModal(this)" class="chatroom-box flex justify-center items-center flex-col border-opacity-50 my-6">
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