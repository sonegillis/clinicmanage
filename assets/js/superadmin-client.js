var clients_to_delete= [];
var total_number;
var number_selected = 0;

$().ready(function() {
    $('input[name="select_client"]').click(function(){
        if($('.select_client:checked').length == $('.select_client').length){
            $('input[name="select_all"]').prop("checked", true);
        }
        else {
            $('input[name="select_all"]').prop("checked", false);
        }
    });

    $('input[name="select_all"]').click(function(){
        if($(this).prop("checked") == true){
            $('input:checkbox').not(this).prop("checked", this.checked);
        }
        else if($(this).prop("checked") == false){
            $('input:checkbox').not(this).prop('checked', this.checked);
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
                    'Successfully Deleted client(s)',
                    'success'
                )
            }
            else{
                var checked_boxes = $('.select_client:checkbox:checked');
                checked_boxes.each(function(){
                    clients_to_delete.push($(this).attr("id"));
                });

                if($("#action").text() != "Delete"){
                    return;
                }
                $.ajax({
                    type            :  'POST',
                    url             :  '/superadmin/delete-client/',
                    data            :  {
                                       "clients_to_delete[]" :  clients_to_delete,
                                       csrfmiddlewaretoken : $("input[name=csrfmiddlewaretoken]").val()
                    },
                    success         :  function(data, textStatus, jqXHR){
                        clients_to_delete = [];
                        location.reload(true);
                    },
                    dataType        : 'HTML'
                });
            }
        });
    });
});