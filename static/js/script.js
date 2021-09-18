$('.message a').click(function() {
    console.log("Hello");
    $('form').animate({ height: "toggle", opacity: "toggle" }, "slow");
});

$('#fileup').change(function() {
    Array.prototype.forEach.call(
        document.querySelectorAll(".file-upload__button"),
        function(button) {
            const hiddenInput = button.parentElement.querySelector(
                ".file-upload__input"
            );
            const label = button.parentElement.querySelector(".file-upload__label");
            const defaultLabelText = "No file(s) selected";

            // Set default text for label
            label.textContent = defaultLabelText;
            label.title = defaultLabelText;

            button.addEventListener("click", function() {
                hiddenInput.click();
            });

            hiddenInput.addEventListener("change", function() {
                const filenameList = Array.prototype.map.call(hiddenInput.files, function(
                    file
                ) {
                    return file.name;
                });

                label.textContent = filenameList.join(", ") || defaultLabelText;
                label.title = label.textContent;
            });
        }
    );

    //here we take the file extension and set an array of valid extensions
    var res = $('#fileup').val();
    var arr = res.split("\\");
    var filename = arr.slice(-1)[0];
    filextension = filename.split(".");
    filext = "." + filextension.slice(-1)[0];
    valid = [".jpg", ".png", ".jpeg", ".bmp"];
    //if file is not valid we show the error icon, the red alert, and hide the submit button
    if (valid.indexOf(filext.toLowerCase()) == -1) {
        $(".imgupload").hide("slow");
        $(".imgupload.ok").hide("slow");
        $(".imgupload.stop").show("slow");

        $('#namefile').css({ "color": "red", "font-weight": 700 });
        $('#namefile').html("File " + filename + " is not  pic!");

        $("#submitbtn").hide();
        $("#fakebtn").show();
    } else {
        //if file is valid we show the green alert and show the valid submit
        $(".imgupload").hide("slow");
        $(".imgupload.stop").hide("slow");
        $(".imgupload.ok").show("slow");

        $('#namefile').css({ "color": "green", "font-weight": 700 });
        $('#namefile').html(filename);

        $("#submitbtn").show();
        $("#fakebtn").hide();
    }
});