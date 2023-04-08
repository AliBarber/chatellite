const API_BASE="https://chatellite.alastair.ax/api/"

var displayed_toasts = []

function message_to_satellite(message){
    $("#initial-message-text").html(message.text);
    var initial_toast = $("#initial-message-toast").toast({
        animation : true,
        autohide : false
    });
    // $("#initial-message-toast").toast("show");
    initial_toast.toast("show");
    displayed_toasts.push(initial_toast);
    
}

function message_from_satellite(id, message){

    // Build the toast html
    var toast_html = `
    <div role='alert' class='toast fade hide' id='satellite-message-${id}'>
    <div class='toast-header'><strong class='mr-auto'>${message.sender}</strong><small>at ${message.exact_time_utc}</small></div>
    <div role='alert' class='toast-body'>
    <p>${message.text}</p>
    </div>
    </div>`;
    $("#satellite-response-container").append(toast_html);
    return $(`#satellite-message-${id}`).toast({
        animation : true,
        autohide : false
    });
    
}


$.getJSON(API_BASE+"catalogue", (data) =>{
    $.each(data.catalogue, (idx, satellite_name) => {
        $("#satellite-name-dropdown").append("<li><a class='dropdown-item' href='#'>"+satellite_name+"</a></li>");
    })
    $("#satellite-name-dropdown").css("max-height","70vh")
    $("#satellite-name-dropdown").css("overflow-y","auto")
    
});

$("#satellite-name-dropdown").on("click","a",function(){
    $(".dropdown-item").removeClass("active");
    $(this).addClass("active");

    $("#start-alert").hide();
    $("#error-alert").hide();
    $("#loading-spinner").show();

    $("#satellite-response-container").empty();
    $.each(displayed_toasts, (idx, existing_toast) => { existing_toast.toast("dispose"); });
    displayed_toasts = [];

    $.getJSON(
        API_BASE+"greeting/"+$(this).text(), (greeting) => {
            // console.log(greeting);
            message_to_satellite(greeting.messages[0]);
        }
    );

    $.ajax({
        dataType: "json",
        url : API_BASE+"conversation/"+$(this).text(),
        success: function(conversation) { 
            $("#loading-spinner").hide();
            displayed_toasts.push(message_from_satellite(i, conversation.messages[0]).toast("show"));
            var i = 1;
            var timeout = setInterval(function(){
                displayed_toasts.push(message_from_satellite(i, conversation.messages[i]).toast("show"));
                i++;
                if(i == conversation.messages.length){
                    clearInterval(timeout);
                }
            }, 800);
        },
        timeout: 10000,
        error: function(jqXHR, status, errorThrown){
            $("#loading-spinner").hide();
            $("#error-alert").show();
        }

    })
});

$("#loading-spinner").hide();
$("#error-alert").hide();

// $('#first-message-container').toast('show');