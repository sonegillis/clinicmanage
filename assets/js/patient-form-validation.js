$(function(){
    $("#patient-form").validate({
        debug: true,
        rules: {
            name : "required",
            birth_date : "required",
            gender : "required",
            tel: "required",
            address: "required"
        },
        submitHandler: function(form){
            $("#submit_form").prop('disabled', true);
            $("#preloader").show();
            form_data = $("#patient-form").serialize();
            $.ajax({
                type : "POST",
                url : '/custom-admin/add-patient/',
                data : form_data,
                dataType : 'json',
                success : function(response){
                    $("#preloader").hide();
                    var msg = response;
                    swal({
                        title: "Please Give this DimeBook ID to the Patient",
                        text: msg.patient_id,
                        type: "success",
                        closeOnClickOutside: false,
                        closeOnEsc: false,
                        allowOutsideClick: false,
                        }).then(function() {
                        // Redirect the user
                        window.location.href = msg.response_url;
                    });
                },
                error: function(response){
                    $("#preloader").hide();
                    alert("failure");
                    //$("#result").html('There is error while submit');
                },               
            //Your code for AJAX Ends
            }); 
            return false;
        },    
    });
});