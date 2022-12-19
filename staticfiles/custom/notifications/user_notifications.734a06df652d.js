var getNotifications = function () {
   
    $.ajax({
        type: "GET",
        url: "/api/notifications/"
    }).done(function (data) {
       
       
        if(typeof(data)!='string'){
              
             populateNotificationList(data, ".notifications-menu");
        }
       
        
    });
};

var populateNotificationList = function (data, selector) {
           
    var headerText = "";
    if (data.length == 1) {
        headerText = "Usted Tiene " + data.length + " notificación.";
    } else {
        headerText = "Usted Tiene " + data.length + " notificaciones."
    }
    
    $(selector).find(".dropdown-menu .header .header_text").text(headerText);

    if (data.length > 0 && $('#delete_notifications').length == 0) {
       
        $( '<button type="button" class="btn btn-success" id="delete_notifications">Eliminar</button>' ).insertAfter(".header_text");
    }

    $(selector).find("a[data-toggle='dropdown'] .label").text(data.length);

    if(data.length>0){
        $(selector).find("a[data-toggle='dropdown'] .label").addClass("bell");
    }

    for (var i = 0; i < data.length; i++) {
        var element_text = data [i].message != null ? data [i].message:'None';
        if(data [i].content_object.status =="pending"|| data [i].content_object.status =="ManeuverComplete" )
            var url = data [i].content_object.absolute_url;
        else
            var url = data [i].content_object.absolute_maneobras_url;

        var listItems = $(".dropdown-menu .menu li");
        var msg_list = []
        listItems.each(function(idx, li) {
             
             msg_list.push($(li).find('a.noti_link').attr('data-id'));
        });

        var idx = $.inArray((data[i].id).toString(), msg_list);
        if (idx == -1) {
          list_element = "<li><a  class='nowrap noti_link' href='" + url + "' name='notification_link' data-id='" + data[i].id + "'> " + element_text + "</a></li>";
         $(selector).find(".dropdown-menu .menu").append(list_element);
        }
         
        
    }
}

$(document).ready(function () {

    getNotifications()


});

// var handler = setInterval(function() {
//     getNotifications()

// }, 10000);


$(document).on('click','a[name="notification_link"]',function(e){
        $.ajax({
        type: "PUT",
        data:{
            status:true
        },
        url: "/notifications/update-status/"+$(this).attr("data-id")
    }).done(function (response) {
       
        // if(response.code==200){
        // }else{
        //     console.log(response.data)
        // }
      
    });
    })

$(document).on('click','#delete_notifications',function(e){

    var listItems = $(".dropdown-menu .menu li");
        var notification_ids = []
        listItems.each(function(idx, li) {
             
             notification_ids.push($(li).find('a.noti_link').attr('data-id'));
        });

        $.ajax({
        type: "POST",
        data:{
            notification_ids:notification_ids
        },
        url: "/notifications/delete_notifications/"
    }).done(function (response) {
       
        if(response.code==200){
            // var href = $(this).attr("data-url"); 
            // document.location = href;  // redirect browser to link 
        }else{
            console.log(response.data)
        }
      
    });
    })
