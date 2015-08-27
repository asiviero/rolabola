(function($) {
  $(document).ready(function() {
    $("input#checkbox-public-group").click(function() {
      var url = "/group/" + $(this).data("group") + "/private"
      ajaxGet(url, function(content){
        //onSuccess
        console.log(content);
      })
    })

    $(".btn-join-group").click(function() {
      var button = $(this)
      var url = $(this).data("url")
      ajaxGet(url, function(content){
        if(content.membership == "true") {
          button.remove()
        } else {
          button.removeClass("blue")
          button.addClass("disabled")
          // If not in search page, change the label
          if("replace_string" in content) {
            button.html(content["replace_string"])
          }
        }
      })
    })

    $(".btn-accept-group,.btn-reject-group").click(function() {
      var button = $(this)
      var url = $(this).data("url")
      ajaxGet(url, function(content){
        button.closest("li").remove()
      })
    })

    $(".btn-nav").click(function() {
      console.log("NAV")
      button_next = $(this).siblings(".btn-next").addBack()
      button_prev = $(this).siblings(".btn-prev").addBack()
      ajaxPost($(this).data("url"), {
        "year" : $(this).data("year"),
        "month" : $(this).data("month"),
        "day" : $(this).data("day"),
        "next" : $(this).data("next"),
        "group" : $(this).data("group")
      }, function(content) {
        console.log(content)
        button_prev.data("year",content.year)
        button_prev.data("month",content.month)
        button_prev.data("day",content.day)
        button_next.data("year",content.year)
        button_next.data("month",content.month)
        button_next.data("day",content.day)
      })
    })

    $(".confirm-container .btn").click(function() {
      var url = $(this).data("url")
      ajaxGet(url, function(content){

      })
    })

    $(".automatic-confirmation-wrapper label").click(function() {
      var url = $(this).siblings("input").addBack().data("url")
      console.log(url)
      ajaxGet(url, function(content){

      })
    })
    $(document).on("marker_dragged",function(e,data){
      console.log(e)
      console.log(data)
      $("#id_address").val(data.address)
      //console.log($(this).text());
    });

  })




})(jQuery)
