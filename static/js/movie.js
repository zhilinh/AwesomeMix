let csrftoken = getCSRFToken();
let movieId, rating;

$(document).ready(function () {
    let elem = document.querySelector('.slider');
    movieId = document.getElementById("movie_id").value;
    rating = document.getElementById("prev_rate").value;

    let options = {indicators: true, height: 200, interval: 6000000};
    let instance = M.Slider.init(elem, options);
    instance.pause();

    $(".my-rating").starRating({
        initialRating: rating,
        strokeColor: '#894A00',
        strokeWidth: 10,
        starSize: 25,
        starShape: 'rounded',
        disableAfterRate: false,
        callback: function (currentRating) {
            rating = currentRating;
            $.ajax({
                url: "/movie/rate",
                type: "POST",
                data: "movieId=" + movieId + "&rating=" + rating + "&csrfmiddlewaretoken=" + csrftoken,
                dataType: "json",
                success: function (response) {
                    if (typeof response === 'undefined' || 'error' in response){
                        alert(response.error);
                    }
                }
            })
        }
    });
});

function getCSRFToken() {
    let cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}