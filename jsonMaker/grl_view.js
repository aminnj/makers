//<xsl:comment><![CDATA[

// Morten Dam Jørgensen, 2012, mdj@mdj.dk : http://mdj.dk

function GrlView (objGrl, html) {
    this.grl = objGrl;
    this.html = html;
}

GrlView.prototype.header = function(parent) {
    // header() prints the meta information available in the GRL file.
    // Name, version, number of events etc..
    
	
	var runlist_anchored = [];

	for (var run_id=0; run_id < this.grl.LumiBlockCollection.length; run_id++){
        var run = this.grl.LumiBlockCollection[run_id].Run;
        runlist_anchored.push('<a href="#'+run+'">'+run+'</a>');
        // this.grl.LumiBlockCollection[run_id].Run);
		
	}
	
    var head = '<div id="header"><h2>'+this.grl.Name+' (<a href='+this.grl.Link+'>raw JSON</a>)</h2><hr/>'
    // + '<div id="version">' + this.grl.Version + '</div>'
	+ '<h2>Recorded '+this.grl.Recorded+' pb<sup>-1</sup> ('+(100.0*this.grl.Recorded/this.grl.Delivered).toFixed(2)+'% of delivered)</h2></div>'
	+ '<div id="runs"><h3>Runs</h3>' + runlist_anchored.join(", ") + '</div>'
    + '<div id="streams"></div>'
    +'</div>'
	+ '<div id="bar">';
    // + '</div><div id="footer"></div>';
	
    $(this.html).html(head);
    
	
	$("#bar", this.html).html('<div><span class="lumiblock lumi_good" title="LB: i">&#160;&#160;&#160;&#160;</span> Good Block &#160; <span class="lumiblock lumi_bad" title="LB: j">&#160;&#160;&#160;&#160;</span> Bad Block</div><br/><div><span id="lb_range_toggle" class="switch">Show LB Ranges</span></div><div id="lumibars"><br/><span id="lb_toggle" class="switch">Show LB numbers</span><div>' +this.lumiline() + '</div></div><div id="lumi_ranges">' + this.lumi_ranges() + '</div>');



	$("#lb_toggle",this.html).click(function(){ 

		if($(this).html() == "Show LB numbers"){
			$("*.lbid").show();
			$("*.lbspaces").hide();
			$(this).html("Hide LB numbers");
		}else{
			$("*.lbid").hide();
			$("*.lbspaces").show();
			$(this).html("Show LB numbers");
		}


		
	});


	$("#lb_range_toggle",this.html).click(function(){ 
		$("#lumibars").toggle();
		$("#lumi_ranges").toggle();

		if ($(this).html() == "Show LB Ranges"){
			$(this).html("Show Graphs");
		} else {
			$(this).html("Show LB Ranges");
		}

	});
    

};

GrlView.prototype.lumi_ranges = function(run_id, html_id){


	var output = '';
	for (var run_id=0; run_id < this.grl.LumiBlockCollection.length; run_id++){
		var bar_html = '<br/><div class="lumi_bar"><span class="run" id="'+this.grl.LumiBlockCollection[run_id].Run+'">Run: ' + this.grl.LumiBlockCollection[run_id].Run + '</span>';
		for (var lb_id=0; lb_id < this.grl.LumiBlockCollection[run_id].Ranges.length; lb_id++){
			bar_html += '<div class="lb_range_line" >From: ' + this.grl.LumiBlockCollection[run_id].Ranges[lb_id].Start + ' to ' + this.grl.LumiBlockCollection[run_id].Ranges[lb_id].End + '</div>';
		}
		bar_html += '</div>';
		output += bar_html;
		
	}



	return output;

};

GrlView.prototype.lumiline = function(run_id, html_id) {
	
	var output = '';
	for (var li=0; li < this.grl.LumiBlockCollection.length; li++) {
		run_id = li;
	
		// Maximum array id
	    var max_id = this.grl.LumiBlockCollection[run_id].Ranges.length - 1;
		// Maximum LB value at max_id
	    var max_lumi = this.grl.LumiBlockCollection[run_id].Ranges[max_id].End;
		// Minimum LB value at array id == 0
	    var min_lumi = this.grl.LumiBlockCollection[run_id].Ranges[0].Start;
    
    		// Fill an array with the same length as the recorded LB periods
	    var lumi_array = [];
	    for (var i=0; i < max_lumi; i++) {
	        lumi_array[i] = false;
	    };



	    for (var i=0; i < this.grl.LumiBlockCollection[run_id].Ranges.length; i++) {
	        var s = this.grl.LumiBlockCollection[run_id].Ranges[i].Start;
	        var e = this.grl.LumiBlockCollection[run_id].Ranges[i].End;

	        for (var j=-1; j < (e-s); j++) {
	            var val =  s + j;
	            lumi_array[val] = true;
	        };

	    };


    
	    var bar_html = '<br/><div class="lumi_bar"><span class="run" id="'+this.grl.LumiBlockCollection[run_id].Run+'">Run: ' + this.grl.LumiBlockCollection[run_id].Run + ' ';
	    var bar_col = '';

        var n_good = 0;
        var n_bad = 0;
        
        
        var state = lumi_array[0];
        var block = '';
        var blocknn = '';
        
	    for (var i=0; i < lumi_array.length; i++) {
		    var lb = i+1;
		    if (lumi_array[i] != state){
		        state = lumi_array[i];
		        if (state) {
    		        bar_col += '<span class="lumiblock lumi_bad"  title="Bad LBs"><span class="lbspaces">'+ blocknn +'</span><span class="lbid">' + block + '</span></span>';
    		        
		        } else {
    		        bar_col += '<span class="lumiblock lumi_good"  title="Good LBs"><span class="lbspaces">'+ blocknn +'</span><span class="lbid">' + block + '</span></span>';    
		        }
		        block = '';		                
		        blocknn = '';
		    }
		    block += " " + lb;
            blocknn += '&#160;';
            
            if (state) {
                n_good += 1;
            } else {
                n_bad += 1;
            };
	    };
	    if (!state) {
	        bar_col += '<span class="lumiblock lumi_bad"  title="Bad LBs"><span class="lbspaces">'+ blocknn +'</span><span class="lbid">' + block + '</span></span>';
	        
        } else {
	        bar_col += '<span class="lumiblock lumi_good"  title="Good LBs"><span class="lbspaces">'+ blocknn +'</span><span class="lbid">' + block + '</span></span>';	            		            
        }
        
        // bar_col += "</span>";
		bar_html += ' <span class="good_eff">'+ lumi_array.length + ' lumi blocks ' + (n_good/lumi_array.length * 100.0).toFixed(2)  + ' % Good</span></span>' + bar_col + "</div>";
		output += bar_html;
		
	};


    $("div.lumi_bar").live("click", function(){
     $("*.lbid", this).toggle();
      $("*.lbspaces", this).toggle();
    });
    
	return output;


};

$(document).ready(function() {
    
});
//]]></xsl:comment>
