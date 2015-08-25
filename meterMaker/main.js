var isAnimating = false;
var rOuterInnerRatio = 0.6;
var fullMeterRadians = 1.2*Math.PI; // angle subtended by whole meter
var fullMeterStart = -0.1*Math.PI; //start angle of meter (0 points to the east, pi/2 points north)
var centerWidthRatio = 0.5; // fraction of width at which to put centerX
var centerHeightRatio = 0.7; // fraction of height at which to put centerY
var rHeightRatio = 0.5; // fraction of height to make the outer radius

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

// takes rgb and fraction, negative to make darker
function getShade(hex, lum) {
    hex = String(hex).replace(/[^0-9a-f]/gi, '');
    if (hex.length < 6) {
        hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
    }
    lum = lum || 0;
    var rgb = "#", c, i;
    for (i = 0; i < 3; i++) {
        c = parseInt(hex.substr(i*2,2), 16);
        c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
        rgb += ("00"+c).substr(c.length);
    }
    return rgb;
}

function drawGraph(canvas, graphDict) {
  var context = canvas.getContext("2d")

  var centerX = canvas.width * centerWidthRatio;
  var centerY = canvas.height * centerHeightRatio;
  var rOuter = canvas.height * rHeightRatio;
  var rInner = rOuter*rOuterInnerRatio;
  
  // reset canvas
  context.clearRect(0, 0, canvas.width, canvas.height);

  // easiest way is to shift everything
  context.translate(centerX,centerY);
  context.rotate(fullMeterStart);
  context.translate(-centerX,-centerY);

  var params = { "rOuter": rOuter, "rInner": rInner, "fullMeterRadians": fullMeterRadians, "fullMeterStart": fullMeterStart, "centerX": centerX, "centerY": centerY };

  var sumFrac = 0.0;
  for(var i = 0; i < graphDict["slices"].length; i++) {
    var slice = graphDict["slices"][i];
    drawSlice(context, sumFrac, sumFrac+slice["fraction"], slice["color"], slice["label"], params);
    sumFrac += slice["fraction"];

  }
  drawPointer(context, graphDict["pointer"], params);

  context.translate(centerX,centerY);
  context.rotate(-fullMeterStart);
  context.translate(-centerX,-centerY);
}

function drawSlice(context, f0, f1, color1, label, params) {
  var rOuter = params["rOuter"];
  var rInner = params["rInner"];
  var fullMeterStart = params["fullMeterStart"];
  var fullMeterRadians = params["fullMeterRadians"];
  var centerX = params["centerX"];
  var centerY = params["centerY"];

  var theta0 = f0*fullMeterRadians+Math.PI;
  var theta1 = f1*fullMeterRadians+Math.PI;

  context.beginPath();
  context.moveTo(centerX-rInner*Math.cos(theta0-Math.PI),centerY-rInner*Math.sin(theta0-Math.PI));
  context.arc(centerX, centerY, rOuter, theta0, theta1, false);
  context.lineTo(centerX-rInner*Math.cos(theta1-Math.PI),centerY-rInner*Math.sin(theta1-Math.PI));

  context.arc(centerX, centerY, rInner, theta1, theta0, true);
  context.closePath();


  var grad = context.createRadialGradient(centerX,centerY,rInner,centerX,centerY,rOuter);
  grad.addColorStop(0.2,getShade(color1, 0.15)); // 15% lighter
  grad.addColorStop(0.7,color1);
  grad.addColorStop(1,getShade(color1, -0.15)); // 15% darker

  // text
  label = label || "";
  context.font = "bold 16px sans-serif";
  context.textAlign = "center";
  context.save();
  context.fillStyle = "#000";
  context.translate(centerX-1.1*rOuter*Math.cos((theta0+theta1)/2-Math.PI),centerY-1.1*rOuter*Math.sin((theta0+theta1)/2-Math.PI));
  context.rotate((theta0+theta1)/2+Math.PI/2);
  context.fillText(label,0,0);
  context.restore();

  context.fillStyle = grad;
  context.fill();
  context.lineWidth = 1;
  context.strokeStyle = '#000';
}

function drawPointer(context, f0, params) {
  var rOuter = 0.75*params["rOuter"]; // note the switchup
  var rInner = 0.08*params["rOuter"]; // just wanted to base it on rOuter
  var fullMeterStart = params["fullMeterStart"];
  var fullMeterRadians = params["fullMeterRadians"];
  var centerX = params["centerX"];
  var centerY = params["centerY"];

  var theta0 = f0*fullMeterRadians+3*Math.PI/2;
  var theta1 = theta0+Math.PI;

  context.beginPath();
  context.moveTo(centerX-rOuter*Math.cos(f0*fullMeterRadians),centerY-rOuter*Math.sin(f0*fullMeterRadians));
  context.arc(centerX, centerY, rInner, theta0, theta1, false);

  context.closePath();

  var grad = context.createRadialGradient(centerX,centerY,0,centerX,centerY,rOuter);
  grad.addColorStop(0,"#fff");
  grad.addColorStop(0.01,"#ddd");
  grad.addColorStop(0.05,"#000");
  grad.addColorStop(0.5,"#000");
  grad.addColorStop(1,"#666");
  context.fillStyle = grad;
  context.fill();
}

