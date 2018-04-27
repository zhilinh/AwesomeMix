let csrftoken = getCSRFToken();
let movieId, rating, status, dltCmmntBtn;

$(document).ready(function () {
    let elem = document.querySelector('.slider');
    dltCmmntBtn = document.getElementById("dlt-cmmnt-btn");
    movieId = document.getElementById("movie_id").value;
    rating = document.getElementById("prev_rate").value;
    // Cannot use the same name as id in html!
    status = document.getElementById("user_wishlist").value === 'True';

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

    // Functions will run AUTOMATICALLY with brackets "()"!!
    addWishlistButton();
    dltCmmntBtn.addEventListener('click', deleteComment);

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

function addWishlistButton() {
    // True in Python is not true in JavaScript
    if (status) {
        $("#add_to_wishlist").append(
            '<a class="btn-floating btn-large waves-effect waves-light" id="wishlist_button" ' +
            'onclick="wishlistOp(1)">' +
            '<i class="material-icons">add</i>' +
            '</a>'
        )
    } else {
        $("#add_to_wishlist").append(
            '<a class="btn-floating btn-large waves-effect waves-light red" id="wishlist_button" ' +
            'onclick="wishlistOp(0)">' +
            '<i class="material-icons">clear</i>' +
            '</a>'
        )
    }
}

function wishlistOp(op) {
    $.ajax({
        url: "/movie/wishlist_op",
        type: "POST",
        data: "movieId=" + movieId + "&op=" + op + "&csrfmiddlewaretoken=" + csrftoken,
        dataType: "json",
        success: function (response) {
            if (typeof response === 'undefined' || 'error' in response) {
                alert(response.error);
            }
        }
    });
    $("#add_to_wishlist").empty();
    status = !status;
    addWishlistButton();
}

function deleteComment() {
    $.ajax({
        url: "/movie/delete_comment",
        type: "POST",
        data: "movieId=" + movieId + "&csrfmiddlewaretoken=" + csrftoken,
        dataType: "json",
        success: function (response) {
            if (typeof response === 'undefined' || 'error' in response) {
                alert(response.error);
            } else {
                let myCmmnt = document.getElementById("my_comment");
                if (myCmmnt !== null) {
                    myCmmnt.remove();
                }
            }
        },
        // IMPORTANT!!
        error: function(requestObject, error, errorThrown) {
            alert(error);
            alert(errorThrown);
       }
    });
}