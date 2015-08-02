(function($) {
  $(document).ready(function() {
    $("input#checkbox-public-group").click(function() {
      var url = "/group/" + $(this).data("group") + "/private"
      ajaxGet(url, function(content){
        //onSuccess
        console.log(content);
    })
    })
  })
})(jQuery)
