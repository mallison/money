(function () {
    $('.editable').click(function (e) {
        var that = $(this);
        display = that.find('.display')
        display.hide();
        that.find('.control_container').show();
        that.find('.control').focus().select();
    });     
    
    $('.editable .close').live('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var editable = $(this).parents('.editable');
        editable.find('.display').show();
        editable.find('.control_container').hide();
    });     
    
    $('.editable .save').live('click', function (e) {
        e.preventDefault();
        var editable = $(this).parents('.editable'),
            form = editable.find('form');
        $.post(form.attr('action'), 
               form.serialize(),
               function (snippet) {
                   editable.html(snippet);
                   // reload the summary panel
                   $('#related').load('/ #related table');
               })
    });     

    // show transactions for a given tag
   $('input[name="tags"]').change(
       // TODO is onchange still broken in IE (element has to lose focus to fire onchange)
       function () {
           // TODO: this is lazy, hiding all then showing one -- use some state!
           $('#transaction-list tr').hide();
           $('tr.' + $(this).val()).show();
       }
   );
   $('#show-all').click(
       function (e) {
           e.preventDefault();
           $('#transaction-list tr').show();
           $('input[name="tags"]:checked').removeAttr("checked");
   });

}());
