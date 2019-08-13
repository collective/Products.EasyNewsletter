(function($) {

$(document).ready(function() {
    var members = '#archetypes-fieldname-ploneReceiverMembers';
    var groups = '#archetypes-fieldname-ploneReceiverGroups';

    if ($('#sendToAllPloneMembers').attr('checked')) {
      $(members).css('visibility', 'hidden');
      $(groups).css('visibility', 'hidden');
    }else {
      $(members).css('visibility', 'visible');
      $(groups).css('visibility', 'visible');
    }
    $('#sendToAllPloneMembers').click(function() {
      if ($(this).attr('checked')) {
        $(members).css('visibility', 'hidden');
        $(groups).css('visibility', 'hidden');
      }else {
        $(members).css('visibility', 'visible');
        $(groups).css('visibility', 'visible');
      }
    });
  });

})(jQuery);
