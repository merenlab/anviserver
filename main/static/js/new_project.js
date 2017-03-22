\var tree;
var viewData;
var header_len;

$(document).ready(function() {
    $('#treeFile').change(function(event) {
        var file = event.target.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var contents = e.target.result;
                tree = new Tree();
                tree.Parse(contents);
                if (tree.error) {
                    $('#txtTreeFile').val('"' + file.name + '" is not a valid newick tree.');
                    $('#txtTreeFile').css('background-color', '#f2dede');
                } else {
                    $('#txtTreeFile').val('"' + file.name + '" loaded. It contains ' + tree.num_leaves + ' leaves. ');
                    $('#txtTreeFile').css('background-color', '#dff0d8');
                }
            }
            reader.readAsText(file);
        }
    });

    $('#dataFile').change(function(event) {
        var file = event.target.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                try {
                    var contents = e.target.result;
                    viewData = Papa.parse(contents, {'delimiter': '\t'})['data'];
                    header_len = viewData[0].length;

                    if (header_len < 2) {
                        throw 'Data file contains less than two columns.';
                    }
/*                    if (viewData[0][0] != 'contig') {
                        throw 'First column of header should "contig", but it is "' + viewData[0][0] + '".';
                    }*/
                    for (var i=0; i < viewData.length - 1; i++)
                    {
                        if (viewData[i].length != header_len) {
                            throw 'Line ' + (i+1) + ' has ' + viewData[i].length + ' columns, but header has ' + header_len + " columns";
                        }
                    }
                    $('#txtDataFile').val('"' + file.name + '" loaded. It contains ' + header_len + ' columns.');
                    $('#txtDataFile').css('background-color', '#dff0d8');
                }
                catch (e) {
                    $('#txtDataFile').val(e);
                    $('#txtDataFile').css('background-color', '#f2dede');
                }
            }
            reader.readAsText(file);
        }
    });

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
        success: function() {
            showPercent('100');
        },
        complete: function(xhr) {
            showPercent('100');
            window.location.href = '/projects';
        }
    }); 

});
