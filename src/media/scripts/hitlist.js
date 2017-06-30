$(document).ready(function(){


$(".toggleEntry").click(function(event){
	var entry = $(this).parent().parent().parent().parent().parent()[0];
	var entry_id = parseInt(entry.id.replace("entry-",""));
	Dajaxice.mylist.toggleEntry(mylist_callback, {'entry_id':entry_id});
	event.preventDefault();
});



});
