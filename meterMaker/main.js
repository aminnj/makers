var isAnimating = false;

$.ajaxSetup({
    type: 'POST',
    timeout: 4000,
});

function toggleMeters() {
    $('#meters').slideToggle(250);
}
function toggleMaker() {
    $('#maker').slideToggle(250);
}

function logMessage(msg,color) {
    if(isAnimating) return; // comment this out if you want to see all messages
    color = color || "black";
    $('#messages').fadeIn(250);
    document.getElementById("messages").innerHTML = "<font color='"+color+"'>"+msg+"</font>";

    isAnimating = true;
    $('#messages').delay(1500).fadeOut( 300, function(obj) { isAnimating = false} );

}

// initializations
$(function() {
  init();
});


function init() {
}

