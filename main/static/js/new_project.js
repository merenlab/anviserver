var tree;

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
                    $('#txtTreeFile').val('"' + file.name + ' is not a valid newick tree.');
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
                    var viewData = Papa.parse(contents, {'delimiter': '\t'})['data'];
                    var layerdata_dict = {};
                    var header_len = viewData[0].length;
                    for (var i=0; i < viewData.length; i++)
                    {
                        layerdata_dict[viewData[i][0]] = viewData[i].slice(0);
                    }
                    for (var i=0; i < tree.nodes.length; i++)
                    {
                        node = tree.nodes[i];
                        if (!node.IsLeaf()) {
                            continue;
                        }
                        if (!layerdata_dict.hasOwnProperty(node.label)) {
                            throw 'There is no data entry for "' + node.label + '".'
                        }
                        if (layerdata_dict[node.label].length != header_len) {
                            throw 'Length of line ' + node.label + ' is different than header. ';
                        }

                    }
                    $('#txtDataFile').val('"' + file.name + '" loaded. It contains ' + header_len + ' columns and matches with tree.');
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
        type: 'post',
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
