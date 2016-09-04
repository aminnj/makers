function prettyJSON(elem, json) {
    var node = new PrettyJSON.view.Node({ 
        el:elem,
        data:json
    });
    node.expandAll();
}

var t0;
function doSubmit(data) {
    $("#loading_animation").show();
    $("#query_container").show();
    prettyJSON($('#query'), data);
    var cli_str = "dis_client.py ";
    if(data["type"] != "basic") cli_str += "-t " + data["type"] + " ";
    if(data["short"] != "short") cli_str += "--detail ";
    cli_str += '"' + data["query"] + '"';
    $('#clisyntax').html(cli_str);
    $("#result_container").hide();
    t0 = new Date().getTime();
    $.get("handler.py", data)
        .done(function(response) {})
        .always(function(response){
            console.log(response);
            if(response["response"]["status"] == "success" && response["response"]["warning"].length == 0) {
                prettyJSON($("#result"), response["response"]["payload"]);
            } else {
                prettyJSON($("#result"), response["response"]);
            }
            $("#loading_animation").hide();
            $("#result_container").show();
            $(".timing").html("loaded in " + (new Date().getTime()-t0)/1000 + " seconds");
    });
}

var examplesVisible = false;
function toggleExamples() {
    $("#examples_container").slideToggle();
    if(examplesVisible) {
        $("#toggle_examples").text("show examples");
        examplesVisible = false;
    } else {
        $("#toggle_examples").text("hide examples");
        examplesVisible = true;
    }

}

$(function(){

    $("#query_container").hide();
    $("#result_container").hide();
    $("#loading_animation").hide();

    $(".submit_button").click(function() {
        var data = {};
        $.each($("#main_form").serializeArray(), function (i, field) { data[field.name] = field.value || ""; });
        console.log(data);
        doSubmit(data);
    });
    
});
