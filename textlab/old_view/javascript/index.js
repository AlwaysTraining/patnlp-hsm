$(function() {
    $(".ts-box h2").click(function() {
        $(this).parent().find(".inner").slideToggle();
    });
    $(".ts-box2 h2").click(function() {
        $(this).parent().find(".inner").slideToggle();
    });
    
    $('body').layout({});
});
