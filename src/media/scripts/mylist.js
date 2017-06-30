mode='mylist';
stack = new Array();

function assign_entry_numbers(){
	var i = 1;
	$(".entry-nr:visible").each(function(index){
			$(this).html(i);
			i++;
		});
	return i - 1;
}

function delete_entries(rows){
	stack.push(rows);
	refresh_undo_button();
	rows.each(function(){
		entry_id = parseInt(this.id.replace("entry-", ""));
		Dajaxice.mylist.toggleEntry(mylist_callback, {'entry_id':entry_id});
	});
	//flash_mylist();
}


function refresh_undo_button(){
	if (stack.length > 0){
		//$("#undo").removeClass("inactive").attr("href", "#");
	} else{
		//$("#undo").addClass("inactive").removeAttr("href");

	}
}
function refresh_delete_button(){
	if ($("div.entry:visible").length > 0){
		//$("#delete-all").removeClass("inactive").attr("href", "#");
	} else{
		//$("#delete-all").addClass("inactive").removeAttr("href");
		location.reload();
	}
}

$(document).ready(function(){
	assign_entry_numbers();



$(".toggleEntry").click(function(event){
	var row = $(this).parent().parent().parent().parent().parent();
	row.fadeOut(200,function(){
		assign_entry_numbers();refresh_delete_button();});
	delete_entries(row);

	event.preventDefault();

});

$("#delete-all").click(function(event){
	$("#delete-all").addClass("inactive").removeAttr("href");
	var rows = $("div.entry:visible");
	delete_entries(rows);
	$("div.entry:visible").fadeOut();
	event.preventDefault();

});

$("#undo").click(function(event){
	var rows = stack.pop();
	rows.each(function(){
		var entry_id = parseInt(this.id.replace("entry-", ""));
		Dajaxice.mylist.toggleEntry(mylist_callback, {'entry_id':entry_id});
	});

	//flash_mylist();
	refresh_delete_button();
	rows.fadeIn(100, refresh_undo_button);
	$("#delete-all").removeClass("inactive").attr("href", "#");
	//rows.effect("highlight", {}, 1000);
	assign_entry_numbers();
	event.preventDefault();
});

});
