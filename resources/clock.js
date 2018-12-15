

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



//
// Refresh UI elements
//
const TAB_HARDWARE = 4;

function createHardware() {
    $("#hardware-load").progressbar({
       value: false,
       max: 1.0
    });

    $("#hardware-temperature").progressbar({
       value: false,
       max: 100.0
    });

    $("#hardware-memory").progressbar({
       value: false,
       max: 1.0
    });
}


function setupRefreshTimer() {
    refresh();
    setInterval(refresh, 2500);
    $("#tabs").on("tabsactivate", refresh);
}

function refresh() {
    console.log("Refreshing");
    var activeTabIndex = $("#tabs").tabs("option", "active");
    var activeTab = $($("#tabs li")[activeTabIndex]).text();
    console.log("Active tab: " + activeTabIndex);

    if (activeTabIndex == TAB_HARDWARE) {
        refreshHardware();
    }

}

function refreshHardware() {
    console.log("Refreshing hardware");
    $.getJSON("/api/hardware", {}).done(function(data) {
        $("#hardware-load").progressbar("value", data.loadavg);
        $("#hardware-load-label").text(data.loadavg);


        $("#hardware-temperature").progressbar("value", data.temperature);
        $("#hardware-temperature-label").text(data.temperature + "ºC");


        $("#hardware-frequency").text(Math.round(data.frequency / (1024 * 1024)) + "Mhz");
        $("#hardware-voltage").text(data.voltage + "V");

        var memoryFree = Math.round(data.free / 1024);
        var memoryTotal = Math.round(data.memory / 1024);
        $("#hardware-memory").progressbar("option", "max", memoryTotal);
        $("#hardware-memory").progressbar("value", memoryFree);
        $("#hardware-memory-label").text(memoryFree + " / " + memoryTotal + " MB");

        $("#hardware-uptime").text(secondsToDhms(data.uptime));
    });
}

$(document).ready(function() {
    createHardware();
    setupRefreshTimer();
});


function secondsToDhms(seconds) {
    seconds = Number(seconds);
    var d = Math.floor(seconds / (3600 * 24));
    var h = Math.floor(seconds % (3600 * 24) / 3600);
    var m = Math.floor(seconds % 3600 / 60);
    var s = Math.floor(seconds % 3600 % 60);

    var dDisplay = d > 0 ? d + (d == 1 ? " day, " : " days, ") : "";
    var hDisplay = h > 9 ? h + ":" : "0" + h + ":";
    var mDisplay = m > 9 ? m + ":"  : "0" + m + ":";
    var sDisplay = s > 9 ? s : "0" + s;
    return dDisplay + hDisplay + mDisplay + sDisplay;
}