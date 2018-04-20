$(document).ready(function(){
    let elem = document.querySelector('.autocomplete');
    let instance = M.Autocomplete.init(elem, options);
    $('.parallax').parallax();

    $('input.autocomplete').autocomplete({
        data: {
            "Apple": null,
            "Microsoft": null,
            "Google": 'https://placehold.it/250x250'
        },
    });
});

/*
window.onload = function () {
    var startPos;
    var geoSuccess = function (position) {
        startPos = position;
        document.getElementById('startLat').innerHTML = startPos.coords.latitude;
        document.getElementById('startLon').innerHTML = startPos.coords.longitude;
    };
    var geoError = function (error) {
        console.log('Error occurred. Error code: ' + error.code);
        // error.code can be:
        //   0: unknown error
        //   1: permission denied
        //   2: position unavailable (error response from location provider)
        //   3: timed out
    };
    navigator.geolocation.getCurrentPosition(geoSuccess, geoError);
};
*/