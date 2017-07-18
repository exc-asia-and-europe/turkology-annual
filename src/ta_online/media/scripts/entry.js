function export_callback(data){
	$("#export-code").remove();
	export_code = data.export_code;
	$("#export-code-container").append('<div id="export-code">'+export_code)+'</div>';
	$("#export-window").show();
}
$(document).ready(function(){



$(".toggle-export-menu").click(function(event){
	$(".export-link").hide();
	$(".export-formats").fadeIn();
	$(this).removeAttr("href");
	event.preventDefault();
});




$(".export-format").click(function(event){
	Dajaxice.mylist.exportEntry(export_callback, {'exp_format':this.id, 'entry_id':entry_id});
	current_format = this.id;
	$("#export-window-format-name").html($(this).html())
	$(".active-format").removeClass("active-format").attr("href", "#");
	$(this).addClass("active-format").removeAttr("href");
	event.preventDefault();
});

$("#export-window-save-button").click(function(event){
	window.location = "/mylist/export_entry/" + entry_id + "/" + current_format;

});

/*$("html").click(function(event){
	var t = event.target;
	if (t.className != "export-format"){
		$("#export-window").hide();
	}
});*/

$("#export-window-close-button").click(function(event){
	$("#export-window").hide();
	$(".active-format").removeClass("active-format").attr("href", "#");
	event.preventDefault();
});

$("#export-window-save-button").click(function(event){
	//$("#export-window").hide();
	event.preventDefault();
});

$("#toggleEntry").click(function(event){
	Dajaxice.mylist.toggleEntry(mylist_callback, {'entry_id':entry_id});
	//flash_mylist();
});
//$(".toggle-export-menu").click();
//$("#ris").click();
});


