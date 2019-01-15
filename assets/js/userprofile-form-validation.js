$(function(){
    $.validator.addMethod('strongPassword', function(value, element){
        return this.optional(element) 
        || value.length >= 8
        && /\d/.test(value)
        && /[a-z]/i.test(value)
    },
    'Your password must atleast 8 characters with atleast one number included'
    );
    $("#userprofile-form").submit(function(e) {
        e.preventDefault();
        $("#add-worker").prop('disabled', true);
    }).validate({
        rules: {
            username: {
                required : true,
                nowhitespace : true,
                remote: {
                    url: window.location.protocol+"//"+window.location.hostname+"/verify-username/",
                    type: "post",
                    data: {
                        username: function() {
                        return $( "#username" ).val();
                        },
                        csrfmiddlewaretoken : $("input[name=csrfmiddlewaretoken]").val()
                    }
                  }            
            },
            last_name : "required",
            first_name : "required",
            tel: "required",
            email : {
                required : true,
                email : true
            },
            profile_pic : {
                required : false,
                accept : "image/*"
            },
            password1: {
                strongPassword : true,
            },
            password2: {
                required : true,
                equalTo : "#password1",
            }
        },
        messages: {
            username: {
                required: "Required",
                remote: "Username is already taken"
            }
        },
        submitHandler: function(form){
            var userprofileForm = document.getElementById('userprofile-form');
            var form_data = new FormData(userprofileForm);
            $.ajax({
                type : "POST",
                url : window.location.href,
                data : form_data,
                cache:false,
                contentType: false,
                processData: false,
                dataType : 'json',
                success : function(response){
                    swal({
                        title: "Succesfully " + response.msg + " " + response.first_name,
                        text: "",
                        type: "success",
                        closeOnClickOutside: false,
                        closeOnEsc: false,
                        allowOutsideClick: false,
                        }).then(function() {
                        // Redirect the user
                        window.location.href = response.url;
                    });                   
                },
                error: function(xhr, status, error){
                    swal({
                        title: "An error occurred",
                        text: "Report this to developer",
                        type: "error",
                        closeOnClickOutside: false,
                        closeOnEsc: false,
                        allowOutsideClick: false,
                        }).then(function() {
                        // Redirect the user
                        window.location.href = xhr.responseText;
                    });
                },               
            //Your code for AJAX Ends
            }); 
            return false;
        },
    });
});