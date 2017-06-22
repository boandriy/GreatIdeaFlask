$(function(){
        $('#btnSignUp').click(function(){

                $.ajax({
                        url: '/signUp_check',
                        data: $('form').serialize(),
                        type: 'POST',
                        success: function(response){
                                console.log(response);
                                alert(response);
                        },
                        error: function(error){
                                console.log(error);
                                alert(error);
                        }
                });
        });
});
