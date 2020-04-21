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

function openClose(targetPercentageOpen) {
    let url = "./Operate?targetPercentageOpen=" + targetPercentageOpen + "&key=" + key + "&timestamp=" + Date.now();
    $.get(url, updateResult);
}

$("#button-open").click(function () {
    openClose(100)
});

$("#button-close").click(function () {
    openClose(0)
});

$("#button-set-to").click(function () {
    openClose($('#target-percentage-select').val())
});

$("#button-current").click(function () {
        $.get("./CurrentPosition?key=" + key, updateResult);
    });

$(function () {
    for (let index = 100; index >= 0; index -= 10) {
        $('#target-percentage-select').append(`<option value="${index}"> ${index} </option>`);
    }
})
