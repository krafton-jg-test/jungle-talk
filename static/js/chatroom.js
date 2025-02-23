
let room_id = 1234;
let user_list = [];
let count =-1;

// # 채팅방에 참여중인 유저 리스트 요청 API -> done
function requestUserData(){
    $.ajax({
        type:"GET",
        url:`/chatrooms/users?chatroom_id=${room_id}`,
        data:{},
        success:function(response){
            if (response['is_success']==1){
                user_list = response['list']
                console.log(users_in_room,response['msg'])
            }else{
                console.log(response['msg'])
            }
        }
    })   
}


$(document).ready( function () {
    requestUserData()
    routine()

    //5초마다 루틴 반복
    setInterval(routine, 5000)
})

// 메세지를 생성하는 함수 -> done
function makeMSG(uuid,message,time) {
    let image = None;
    let name = None;
    for( let item in users_in_room){
        if(item['uuid'] == uuid){
            image = item['user_image'];
            name = item['user_name'];
        }
    }

    if (logined_uuid != uuid) {
        temp_tag=
            `<div class="chat chat-start">
        <div class="chat-image avatar">
            <div class="w-10 rounded-full">
                <img alt="Tailwind CSS chat bubble component"
                    src="${image}"/>
            </div>
        </div>
            <div class="chat-header">
                ${name}
                <time class="text-xs opacity-50">${time}</time>
            </div>
            <div class="chat-bubble">${message}</div>
    </div>`;
    } else {
        temp_tag=`
        <div class="chat chat-end">
        <div class="chat-image avatar">
            <div class="w-10 rounded-full">
                <img alt="Tailwind CSS chat bubble component"
                    src="${image}"/>
            </div>
        </div>
        <div class="chat-header">
            ${name}
            <time class="text-xs opacity-50">${time}</time>
        </div>
        <div class="chat-bubble">${message}</div>
        </div>`;
    }
    $('#chat-box').append(temp_tag);
}

// 새로운 메세지를 추가하는 메소드 
function addMSG() {
    let chat_box = $("#chat-box")
    $.ajax({
        type:"POST",
        url:"/chat/chatrooms/messages",
        data : {
            'chatroom_id':1234,
            'message':"test"
        },
        success : function(response){
           console.log(response)
        }
    })
    console.log("test")
}

// # 특정 채팅방의 채팅기록 요청 API -> done
function routine(){
    $.ajax({
        type:"GET",
        url:`/chat/chatrooms/messages?chatroom_id=${room_id}&count=${count}`,
        data : {},
        success : function(response){
            if (response['is_success'] == 1){
                let list = response['list'];
                for(let item in list ){
                    makeMSG(item['uuid'],item['message'],item['time'])
                }
                count = response['count'];
                console.log(response['msg'])
                // 새로운 메세지 알림 기능 
            }else if (response['is_success']==0){
                count = response['count'];
                console.log(count,response['is_success'],response['msg'])
            }
        }
    });
    console.log('routine')
}

