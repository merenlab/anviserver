$(document).ready(function() {
    

    function showPercent(percent) {
        $('#modalUploading .modal-header').text('Uploading... (' + percent +'%)');
        $('#modalUploading .progress-bar').css('width', percent + '%');        
    }

    $('form').ajaxForm({
        beforeSend: function() {
            $('#modalUploading').modal();
            showPercent(0);
        },
        uploadProgress: function(event, position, total, percentComplete) {
            showPercent(percentComplete);
        },
        success: function(data) {
            showPercent('100');
            if (data['status'] == 0) {
                window.location.href = '/projects';
            } else {
                $('#modalUploading').modal('hide'); 
                $('#error_box').show();
                $('#error_box').html(data['message']);
            }
        },
        complete: function(xhr) {
            showPercent('100');
        }
    }); 

});
