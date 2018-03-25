// construct the url with parameter values
var apikey = "ebjchzwxwdhyhprsh3ck5sys";
var baseUrl = "http://data.tmsapi.com/v1.1";
var showtimesUrl = baseUrl + '/movies/showings';
var zipCode = "15213";
var d = new Date();
var today = d.getFullYear() + '-' + (d.getMonth()+1) + '-' + d.getDate();

$(document).ready(function() {
    // send off the query
    $.ajax({
        url: showtimesUrl,
        data: {	startDate: today,
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
    var movies = data.hits;
    for (var i = 0; i < 10; i++) {
        // var movieData = '<div class="tile"><img src="http://developer.tmsimg.com/' + movie.preferredImage.uri + '?api_key='+apikey+'"><br/>';
        var movie = data[i];
        var movieData = movie.title;
        if (movie.ratings) { movieData += ' (' + movie.ratings[0].code + ') </div>' }
        $(document.body).append(movieData);
    }
}
