
if ($("#sidebar-menu, #customize-menu").metisMenu({
        activeClass: "open"
    }), $("#sidebar-collapse-btn").on("click", function(e) {
        e.preventDefault(), $("#app").toggleClass("sidebar-open")
    }), $("#sidebar-overlay").on("click", function() {
        $("#app").removeClass("sidebar-open")
    }), $.browser.mobile) {
    var e = $("#app ");
    $("#sidebar-mobile-menu-handle ").swipe({
        swipeLeft: function() {
            e.hasClass("sidebar-open") && e.removeClass("sidebar-open")
        },
        swipeRight: function() {
            e.hasClass("sidebar-open") || e.addClass("sidebar-open")
        },
        triggerOnTouchEnd: !1
    })
}
