function toggleCreateBet() {
    $('#createBet').slideToggle(250);
}
function toggleBets() {
    $('#bets').slideToggle(250);
}
function toggleUsers() {
    $('#users').slideToggle(250);
}

function logMessage(msg,color) {
    color = color || "green";
    $('#messages').fadeIn(250);
    document.getElementById("messages").innerHTML = "<font color='"+color+"'>"+msg+"</font>";
    $('#messages').delay(1500).fadeOut(500);
}

var numBeers = 0;
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
