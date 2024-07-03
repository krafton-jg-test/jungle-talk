let idCheck = 0;
//회원가입
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
    console.log(data);
    $.ajax({
        type: "POST",
        url: "/signup",
        data:post_data,
        success: function(response){
            alert(response['msg'])
        }
    }) 
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


$(document).ready(function(){
    //회원가입 이벤트 등록
    $('#sign-btn').on('click',function(){
        register()
    })
    $('')
})


