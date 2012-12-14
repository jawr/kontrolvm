/* https://github.com/ifightcrime/bootstrap-growl */

(function($) {

  $.bootstrapGrowl = function(message, options) {

    var options = $.extend({}, $.bootstrapGrowl.default_options, options);

    var $alert = $('<div>');

    $alert.attr('class', 'bootstrap-growl alert');

    if (options.type) {
        // parse enum
        if (options.type == '125' || options.type == '25') {
          options.type = 'success';
        }
        else if (options.type == '120' || options.type == '20') {
          options.type = 'info';
        }
        else if (options.type == '130' || options.type == '30') {
          options.type = 'warning';
        }
        else if (options.type == '140' || options.type == '40') {
          options.type = 'error';
        }
        $alert.addClass('alert-' + options.type);
    }

    if (options.allow_dismiss) {
      $alert.append('<a class="close" data-dismiss="alert" href="' + options.read_url + '">&times;</a>');
    }

    $alert.append(message);

    // Prevent BC breaks
    if (options.top_offset) {
        options.offset = {from: 'top', amount: options.top_offset};
    }
    var current = $('.bootstrap-growl', options.ele);

    // calculate any 'stack-up'
    offsetAmount = options.offset.amount;
    $.each(current, function() {
        offsetAmount = offsetAmount + $(this).outerHeight() + options.stackup_spacing;
    });

    css = {
      'position': 'absolute',
      'margin': 0,
      'z-index': '9999',
      'display': 'none'
    };
    css[options.offset.from] = offsetAmount + 'px';
    $alert.css(css);

    if (options.width !== 'auto') {
      $alert.css('width', options.width + 'px');
    }

    // have to append before we can use outerWidth()
    $(options.ele).append($alert);

    switch(options.align) {
      case 'center':
        $alert.css({
          'left': '50%',
          'margin-left': '-' + ($alert.outerWidth() / 2) + 'px'
        });
        break;
      case 'left':
        $alert.css('left', '20px');
        break;
      default:
        $alert.css('right', '20px');
    }

    $alert.fadeIn();
    // Only remove after delay if delay is more than 0
    if(options.delay >= 0){
      $alert.delay(options.delay).fadeOut('slow', function() {
        $(this).remove();
      });
    }

  };

  $.bootstrapGrowl.default_options = {
    ele: 'body',
    type: null,
    offset: {from: 'top', amount: 20},
    align: 'right', // (left, right, or center)
    width: 250,
    delay: 7000,
    allow_dismiss: true,
    stackup_spacing: 10,
    read_url: '#'
  };

})(jQuery);
