function GetURLParameter(sParam) {
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return sParameterName[1];
        }
    }
}

function updateResult(data) {
    $("#result").html(data);
}
let key = GetURLParameter('key');

function openClose(direction) {
    let url = "./Operate?direction=" + direction + "&key=" + key + "&timestamp=" + Date.now();
    $.get(url, updateResult);
}

$("#button-open").click(function () {
    openClose("Open")
}
);

$("#button-close").click(function () {
    openClose("Close")
}
);

$("#button-current").click(function () {
    $.get("./CurrentPosition?key=" + key, updateResult);
}
);
