let csrftoken = getCSRFToken();
let latestText;

$(document).ready(function(){
    latestText = document.getElementById("bio_text").value.toString();
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

function editBio() {
    displayError('');
    let bio = $("#bio_div");
    let text = latestText;

    bio.empty();
    bio.append('<div id=\"bio_div\" class=\"input-field\">' +
        '<textarea id="bio_content" class="materialize-textarea white-text"></textarea>' +
        '<label class="active" for=\"textarea1\">Bio</label>' +
        '</div>');
    // Add quote marks!! Otherwise it might be considered as variables.
    // And fails if a parameter string has space
    bio.append('<a class="btn" onclick=submitBio()>Submit</a><p></p>' +
    '<a class="btn" onclick="cancelBio(\''+ text +'\')">Cancel</a>');
}

function submitBio() {
    displayError('');
    let text = document.getElementById("bio_content").value.toString();
    latestText = text;

    $.ajax({
        url: "/homepage/profile/update_bio",
        type: "POST",
        data: "text=" + text + "&csrfmiddlewaretoken=" + csrftoken,
        dataType: "json",
        success: function () {
            cancelBio(text);
        }
    });
}

function cancelBio(text) {
    let bio = $("#bio_div");
    bio.empty();
    bio.append('<p id="bio_content">'+ text +'</p>' +
        '<a class="btn" onclick=editBio()>Edit</a>');
}

function displayError(message) {
    $("#error").html(message);
}