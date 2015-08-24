var numBeers = 1;
var isAnimating = false;
var bets = [];
var users = [];
var ibetOld = -1;
var ioptOld = -1;

$.ajaxSetup({
    type: 'POST',
    timeout: 4000,
});

function toggleCreateBet() {
    $('#createBet').slideToggle(250);
}
function toggleBets() {
    $('#bets').slideToggle(250);
}
function toggleAddBet() {
    $('#addBet').slideToggle(250);
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
function loadUsers() {
    $.ajax({
            url: "./handler.py",
            type: "POST",
            data: { "action": "getUsers" },
            dataType: "json", 
            success: function(data) {
                    logMessage("Successfully loaded user information", "green");
                    users = data["users"];
                    console.log(data);
                    populateUsers();
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

function addBet() {
    $.ajax({
            url: "./handler.py",
            type: "POST",
            data: {"action":"addBet", "amount":numBeers, "name":$('#addName').val(), "ibet":ibetOld, "iopt":ioptOld},
            success: function(data){
                    logMessage(data);
                    if(data.indexOf("Success") > -1) {
                      loadBets();
                      loadUsers();
                    }
                },
            error: function(data){
                    logMessage("Error connecting to CGI script.","red");
                    console.log(data);
                },
       });

}

function addBetPanel(ibet, iopt) {
  //only toggle if we click on the same "add bet"
  if((ibet == ibetOld && iopt == ioptOld) || (ibetOld == -1 && ioptOld == -1)) {
    toggleAddBet();
  }

  ibetOld = ibet;
  ioptOld = iopt;

  var content = "";
  content += "Casting bet for option <b>" + bets[ibet]["options"][iopt]["name"] + "</b> of bet <b>"+bets[ibet]["shortTitle"]+"</b>";
  $("#addBetText").html(content);

}

function populateBets() {
  var contents = "";
  for(var ibet = 0; ibet < bets.length; ibet++) {
    contents += "<span class='thick'>"+(ibet+1)+".</span> &emsp;";
    contents += "<span onClick='$(\"#betOptions"+ibet+"\").slideToggle()' >";
    contents += bets[ibet]["shortTitle"] + "</span>";

    contents += "<ul id='betOptions"+ibet+"' ";
    // contents += " style='display:none;' "; // XXX REENABLE TO HIDE BY DEFAULT
    contents += " > ";

    options = bets[ibet]["options"];
    for(var iopt = 0; iopt < options.length; iopt++) {
      option = options[iopt];
      contents += "<li id='bet"+ibet+"Options"+iopt+"' >"; // e.g., id="bet0Options2"
      contents += "[ <a href='#' onClick='javascript:addBetPanel("+ibet+","+iopt+")'>add bet</a> ] &ensp;";
      contents += option["name"] + ": &ensp;";

      for(var ibetter = 0; ibetter < option["betters"].length; ibetter++) {
        if(ibetter > 0) contents += ",";
        contents += "&ensp; <b>" + option["betters"][ibetter] + "</b> (" + option["amounts"][ibetter] + ")";

      }

      contents += "</li>";
    }
    contents += "</ul>";

    contents += "<br>";
    console.log(contents);

  }
  $("#betList").html(contents);

}

function populateUsers() {
  var contents = "";

  contents += "<ul>";
  for(var iuser = 0; iuser < users.length; iuser++) {
    contents += "<li>";
    contents += "<b>"+users[iuser][0]+"</b> has bet ";
    contents += "<b>"+users[iuser][1]+"</b> beers in total";
    contents += "</li>";
  }
  contents += "</ul>";
  $("#users").html(contents);

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
  loadUsers();
}

