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
    // $("#result").html(data);
    $("#pos-luifel").html(data['position_luifel']);
    $("#pos-screen").html(data['position_screen']);
}
let key = GetURLParameter('key');

function openClose(targetPercentageOpen) {
    let url = "./Operate?targetPercentageOpen=" + targetPercentageOpen + "&key=" + key + "&timestamp=" + Date.now();
    $.get(url, updateResult);
}

function openCloseScreen(targetPercentageOpen) {
    let url = "./Operate_screen?targetPercentageOpen=" + targetPercentageOpen + "&key=" + key + "&timestamp=" + Date.now();
    $.get(url, updateResult);
}


$("#button-open").click(function () {
    openClose(100)
});

$("#button-close").click(function () {
    openClose(0)
});

$("#button-open-screen").click(function () {
    openCloseScreen(100)
});

$("#button-close-screen").click(function () {
    openCloseScreen(0)
});

$("#button-set-to").click(function () {
    openClose($('#target-percentage-select').val())
});

$("#button-current").click(function () {
    $.get("./CurrentPosition?key=" + key, updateResult);
});

$("#button-mode").click(function () {
    $.post("./Automatic?key=" + key, updateMode);
});

$("#button-mode-screen").click(function () {
    $.post("./Automatic_screen?key=" + key, updateMode);
});

function updateMode(data) {
    $("#span-mode").text(data['automatic_mode']);
    $("#span-mode-screen").text(data['automatic_mode_screen']);
}

$(function () {
    for (let index = 100; index >= 0; index -= 10) {
        $('#target-percentage-select').append(`<option value="${index}"> ${index} </option>`);
    }
    $.get("./Automatic?key=" + key, updateMode);
    $.get("./CurrentPosition?key=" + key, updateResult);
    setInterval(updateChecks(), 10000);
})

function updateChecks() {
    $.get("./get_currentStatusSolarManager?key=" + key, (data) => {
        var checks = unpackToBooleanArray(data, 5);
        setSpanCheckmark("check-own_ok", checks[0]);
        setSpanCheckmark("check-sm_OK", checks[1]);
        setSpanCheckmark("check-solarEdge_OK", checks[2]);
        setSpanCheckmark("check-tm_OK", checks[3]);
        setSpanCheckmark("check-wind_OK", checks[4]);
    });
}

function setSpanCheckmark(span_id, checked) {
    var sign = checked ? "✔️" : "❌";
    $("#" + span_id).text(sign);
}


function unpackToBooleanArray(unpackableInt, numValues) {
    var boolArr = [];
    for (let index = numValues - 1; index >= numValues; index--) {
        var result = (unpackableInt >> index & 1) === 1;
        boolArr.push(result);
    }

    return boolArr;
}
