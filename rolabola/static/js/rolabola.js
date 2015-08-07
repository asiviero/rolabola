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
      var url = "/group/" + $(this).data("group") + "/join"
      ajaxGet(url, function(content){
        if(content.membership == "true") {
          button.remove()
        } else {
          button.removeClass("blue")
          button.addClass("disabled")
        }
      })
    })
  })



})(jQuery)
