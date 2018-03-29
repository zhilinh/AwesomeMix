// construct the url with parameter values
var apikey = "{{ api_key }}";
var baseUrl = "http://data.tmsapi.com/v1.1";
var showtimesUrl = baseUrl + '/movies/showings';
var zipCode = "15213";
var d = new Date();
var today = d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();

$(document).ready(function () {
    // send off the query
    $.ajax({
        url: showtimesUrl,
        data: {
            startDate: today,
            zip: zipCode,
            jsonp: "dataHandler",
            api_key: apikey
        },
        dataType: "jsonp"
    });
});

// callback to handle the results
function dataHandler(data) {
    // $(document.body).append('<p>Found ' + data.length + ' movies showing within 5 miles of ' + zipCode+':</p>');
    var count = 0;
    $.each(data, function (index, movie) {
        // var movieData = '<div class="tile"><img src="http://developer.tmsimg.com/' + movie.preferredImage.uri + '?api_key='+apikey+'"><br/>';
        var movieData = "<a href='#' class='collection-item'>" + movie.title + "(" + movie.ratings[0].code + ")</a>";
        $(document.getElementById("now-playing-movies")).append(movieData);
        if (count < 9) {
            count++;
        } else {
            return false;
        }
    });
}

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