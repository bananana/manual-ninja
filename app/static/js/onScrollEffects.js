function onLoad() {
    window.onscroll = function() {
        // Only show "Back to top" button if content is longer than screen.
        if (document.getElementsByTagName("html")[0].scrollTop > 0) {
            document.getElementById("back-to-top").style.display = "block";
        }
        // Hide "Back to top" button if user is already at the top of the page.
        else {
            document.getElementById("back-to-top").style.display = "none";
        }
    }
}
