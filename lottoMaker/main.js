var numBeers = 1;
var isAnimating = false;
var bets = [];

$.ajaxSetup({
    type: 'POST',
    timeout: 2000,
});

function toggleCreateBet() {
    $('#createBet').slideToggle(250);
}
function toggleBets() {
    $('#bets').slideToggle(250);
}
function toggleAddBet() {
    $('#bets').slideToggle(250);
}
function toggleUsers() {
    $('#users').slideToggle(250);
}

function logMessage(msg,color) {
    if(isAnimating) return; // comment this out if you want to see all messages
    color = color || "black";
    $('#messages').fadeIn(250);
    document.getElementById("messages").innerHTML = "<font color='"+color+"'>"+msg+"</font>";

    isAnimating = true;
    $('#messages').delay(1500).fadeOut( 300, function(obj) { isAnimating = false} );

}

function loadBets() {
    $.ajax({
            url: "./handler.py",
            type: "POST",
            data: { "action": "getBets" },
            dataType: "json", 
            success: function(data) {
                    logMessage("Successfully loaded bet information", "green");
                    bets = data["bets"];
                    console.log(data);
                    populateBets();
                },
            error: function(data) {
                    logMessage("Error connecting to CGI script.","red");
                    console.log(data);
                },
       });
}

function createBet() {
    var formObj = {};
    formObj["action"] = "createBet";
    var inputs = $("#createBet_form").serializeArray();
    $.each(inputs, function (i, input) {
        formObj[input.name] = input.value;
    });
    $.ajax({
            url: "./handler.py",
            type: "POST",
            data: formObj,
            success: function(data){
                    logMessage(data);
                    loadBets();
                },
            error: function(data){
                    logMessage("Error connecting to CGI script.","red");
                    console.log(data);
                },
       });
}

function changeBeers(delta) {
    numBeers += delta;
    if(numBeers < 1) {
        numBeers = 1;
        logMessage("You can't bet nothing...","red");
    }
    if(numBeers > 10) {
        numBeers = 10; // woah there cowboy
        logMessage("Woah there, cowboy! 10 is the max.","red");
    }

    document.getElementById("beers").innerHTML = "("+numBeers+" unit";
    if(numBeers>1) document.getElementById("beers").innerHTML += "s";
    document.getElementById("beers").innerHTML += ") ";

    for(var i=0; i<numBeers; i++) {
        document.getElementById("beers").innerHTML += "<img src='images/bottle.png' style='height:35px;vertical-align:middle' />"
    }
}

function populateBets() {
  var contents = "";
  for(var ibet = 0; ibet < bets.length; ibet++) {
    contents += "<span class='thick'>"+(ibet+1)+".</span> &emsp;";
    contents += "<span onClick='$(\"#betOptions"+ibet+"\").slideToggle()' >";
    contents += bets[ibet]["shortTitle"] + "</span>";


    contents += "<ul id='betOptions"+ibet+"' ";
    // XXX REENABLE TO HIDE BY DEFAULT
    // contents += " style='display:none;' ";
    contents += " > ";

    options = bets[ibet]["options"];
    for(var iopt = 0; iopt < options.length; iopt++) {
      option = options[iopt];
      // e.g., id="bet0Options2"
      contents += "<li id='bet"+ibet+"Options"+iopt+"' >";
      contents += "[ <a href='#' onClick=''>add bet</a> ] &ensp;";
      // contents += " [ add bet ] [ info ] ";
      contents += option["name"];
      contents += "</li>";
    }
    contents += "</ul>";

    contents += "<br>";
    console.log(contents);

  }
  $("#betList").html(contents);

}


// initializations
$(function()
{
  init();

  // enable tooltips in the createBet div
  $( "#createBet" ).tooltip({tooltipClass: "ui-tooltip"});
});


function init() {
  changeBeers(0);
  loadBets();
  // populateBets(bets);
}



