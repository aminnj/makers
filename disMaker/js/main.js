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
    $("#result_container").hide();
    t0 = new Date().getTime();
    $.post("handler.py", data)
        .done(function(response) {})
        .always(function(response){
            $("#loading_animation").hide();
            $("#result_container").show();
            console.log(response);
            if(response["response"]["status"] == "success") {
                prettyJSON($("#result"), response["response"]["payload"]);
            } else {
                prettyJSON($("#result"), response["response"]);
            }
            $("#result_container").show();
            console.log(response);
            $(".timing").html("loaded in " + (new Date().getTime()-t0)/1000 + " seconds");
    });
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
    
    // var data = {"type":"basic", "short": "short", "dataset":"/TChi*/namin-TChi*miniAOD*/USER"};
    // var data = {"type":"files", "short": true, "dataset":"/DYJetsToLL_M-50_Zpt-150toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM"};
    // var data = {"type":"mcm", "dataset":"/DYJetsToLL_M-50_Zpt-150toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM"};
    // doSubmit(data);


});
