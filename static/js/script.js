$('.message a').click(function() {
    console.log("Hello");
    $('form').animate({ height: "toggle", opacity: "toggle" }, "slow");
});