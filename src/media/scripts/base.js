var mode = '';

function flash_mylist(){
	/*var highlightBg = "#FFFF9C";
	var animateMs = 15;*/
	var originalBg = "#3c3c3b";
	//$("#navi-mylist").stop().css("background-color", originalBg).effect("highlight", {}, 1000);

	//$("#navi-mylist").stop().css("background-color", highlightBg).animate({backgroundColor: originalBg}, animateMs);

}


function mylist_callback(data){
        var count = data.mylist_count;
        if (count > 0){
                document.getElementById('list_count').innerHTML = " (" + count + ")";
        }else{
                document.getElementById('list_count').innerHTML = "";
        }

        var id = data.id;
        var added = data.added;
        var caption;
        if (mode == 'mylist'){
                caption = mylist_messages[1];
                document.getElementById('mylist-image-' + id).src = "/site_media/images/remove.png";
        } else{
		flash_mylist();
	        if (added){
	                caption = mylist_messages[1];
	                document.getElementById('mylist-image-' + id).src = "/site_media/images/checked.png";
		} else{
			caption = mylist_messages[0];
			document.getElementById('mylist-image-' + id).src = "/site_media/images/unchecked.png";
	        }
	}

	$('#mylist-image-' + id).attr("title", caption); 
        $('#mylist-text-' + id).html(caption);


}





