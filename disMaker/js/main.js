function prettyJSON(elem, json) {
    var node = new PrettyJSON.view.Node({ 
        el:elem,
        data:json
    });
    node.expandAll();
}
function doSubmit(data) {
    $("#loading_animation").show();
    $("#query_container").show();
    prettyJSON($('#query'), data);
    $("#result_container").hide();
    $.post("handler.py", data).done(function(response) {
    }).always(function(response){
        $("#loading_animation").hide();
        $("#result_container").show();
        prettyJSON($("#result"), response["response"]["payload"]);
        $("#result_container").show();
        console.log(response);

    });
}

$(function(){

    $("#query_container").hide();
    $("#result_container").hide();
    $("#loading_animation").hide();

    var data = {"type":"basic", "short": true, "dataset":"/DYJetsToLL_M-50_Zpt-150toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM"};
    // var data = {"type":"files", "short": true, "dataset":"/DYJetsToLL_M-50_Zpt-150toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM"};
    // var data = {"type":"mcm", "dataset":"/DYJetsToLL_M-50_Zpt-150toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM"};

    $(".submit_button").click(function() {
        var data = {};
        $.each($("#main_form").serializeArray(), function (i, field) { data[field.name] = field.value || ""; });
        console.log(data);
        doSubmit(data);
    });


});
