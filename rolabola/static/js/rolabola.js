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
    $(".geoposition-widget").on("marker_dragged",function(e,data){
      console.log(e)
      console.log(data)
      $("#id_address").val(data.address)
      //console.log($(this).text());
    });

    $('.modal-trigger').leanModal();

    $("#id_venue-dialog a.modal-submit").click(function() {
      var url = $(this).data("url")
      var container = $(this).closest("#id_venue-dialog")
      var data = {
        "address" : $(container).find("#id_address").val(),
        "quadra" : $(container).find("#id_quadra").val(),
        "location_0" : $(container).find("#id_location_0").val(),
        "location_1" : $(container).find("#id_location_1").val()
      }
      ajaxPost($(this).data("url"), data, function(content) {
        container.find(":input").val("")
        container.closeModal()
        $("#id_venue").val(content.id).change();
        $("#id_venue").trigger('contentChanged');
        $("#id_venue").material_select();
      })

    });
    /*$('a[name=add_dialog]').click(function() {
    var dialog, id;
    id = $(this).data('id');
    dialog = $('#' + id + '-dialog').dialog();
    return false;
  });
  return $('input[name=add_another_id_series]').click(function() {
    var data, form;
    form = $(this).parent().parent().find('#form-dialog');
    data = {
      param1: $('#param1').val(),
      param2: $('#param2').val(),
      param3: $('#param3').val(),
      param4: $('#param4').val(),
      param5: $('#param5').val()
    };
    return $.ajax($(this).data('url'), {
      type: 'POST',
      beforeSend: function(request) {
        request.setRequestHeader('Cache-Control', 'no-cache');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        return request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
      },
      data: data,
      success: function(data) {
        if (data.status === 'Wrong') {
          $(form).html(data.form);
        }
        if (data.status === 'Ok') {
          $('#id_series').append('<option value="' + data.id + '">' + data.name + '</option>');
          $('#id_series').val(data.id);
          $('#id_series-dialog').dialog('close');
        }
      }
    });
  });*/
  })




})(jQuery)
