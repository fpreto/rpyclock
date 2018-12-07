$(function () {
    $("#tabs").tabs();
});

$.getJSON("/api/version", {})
    .done(function(data) {
    $("#version").text("Raspberry Pi Wifi Clock v." + data.version);
})
    .fail(function(data) {
    $("#version").text("Raspberry Pi Wifi Clock. Unknown error due API failure");
});
