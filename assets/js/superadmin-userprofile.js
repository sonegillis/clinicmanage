var users_to_delete= [];
var total_number;
var number_selected = 0;

$().ready(function() {
    $('input:checkbox').prop("checked", false);
    $('input[name="select_user"]').click(function(){
        if($(this).prop("checked") == true){
            number_selected++;
            $("#num_of_selected_workers").text(number_selected);
        }
        else{
            number_selected--;
            $("#num_of_selected_workers").text(number_selected);
        }

        if($('.select_user:checked').length == $('.select_user').length){
            $('input[name="select_all"]').prop("checked", true);
        }
        else {
            $('input[name="select_all"]').prop("checked", false);
        }
    });

    $('input[name="select_all"]').click(function(){
        if($(this).prop("checked") == true){
            $('input:checkbox').not(this).prop("checked", this.checked);
            number_selected = num_of_workers;
            $("#num_of_selected_workers").text(number_selected);
        }
        else if($(this).prop("checked") == false){
            $('input:checkbox').not(this).prop('checked', this.checked);
            number_selected = 0;
            $("#num_of_selected_workers").text(number_selected);
        }
    });

    $("#go").click(function(){
        swal({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            type: 'warning',
            closeOnClickOutside: false,
            closeOnEsc: false,
            allowOutsideClick: false,
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
          }).then((result) => {
            if (result.value) {
                swal(
                    'Deleted!',
                    'Successfully Deleted',
                    'success'
                )
            }
            else{
                var checked_boxes = $('.select_user:checkbox:checked');
                checked_boxes.each(function(){
                    users_to_delete.push($(this).attr("id"));
                });

                if($("#action").text() != "Delete"){
                    return;
                }
                $.ajax({
                    type            :  'POST',
                    url             :  '/superadmin/delete-admin/',
                    data            :  {
                                    "users_to_delete[]" :  users_to_delete,
                                    csrfmiddlewaretoken : $("input[name=csrfmiddlewaretoken]").val()
                    },
                    success         :  function(data, textStatus, jqXHR){
                        users_to_delete = [];
                        location.reload(true);
                    },
                    dataType        : 'HTML'
                });
            }
        });
    });
});