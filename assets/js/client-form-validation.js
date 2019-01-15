$(function(){
    $("#client-form").submit(function(e) {
        e.preventDefault();
        $("#add-client").prop('disabled', true)
    }).validate({
        rules: {
            address: "required",
            tel: "required",
            email : {
                required : true,
                email : true,
            },
            clinic_logo : {
                required : false,
                accept : "image/*"
            },
            client_name : "required",
        },
        submitHandler: function(form){
            var clientForm = document.getElementById('client-form');
            var form_data = new FormData(clientForm);
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
                        title: "Succesfully " + response.msg + " " + response.client_name,
                        text: "",
                        type: "success",
                        closeOnClickOutside: false,
                        closeOnEsc: false,
                        allowOutsideClick: false,
                        }).then(function() {
                        // Redirect the user
                        window.location.href = "/superadmin/clients/";
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
                        window.location.href = "/superadmin/clients/";
                    });
                },               
            //Your code for AJAX Ends
            }); 
            return false;
        },
    });
});