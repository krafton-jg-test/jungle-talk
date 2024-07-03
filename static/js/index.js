$(document).ready( function() {
    
    $('.chat-box').on('click',function() {
        let chatroom_id = 1234;
        let chatroom_pw = 1234;
        let uuid =1234;
        console.log('test');
        $.ajax({
            type:"POST",
            url:'chatrooms/enter',
            data:{
                'chatroom_id':chatroom_id,
                'chatroom_pw':chatroom_pw,
                'uuid':uuid
            },
            success:function(response){
                window.location.href= response
                
                console.log(response);
                
            }
        })
    });
});