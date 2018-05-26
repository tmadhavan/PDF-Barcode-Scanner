function emailIsValid(emailAddressInput) {
    console.log("Checking email");
    if (emailAddressInput.value == undefined || emailAddressInput.value == "") {
        return false;
    }
    return true;
}
function uploadFile() {
    var emailAddressInput = document.getElementById("email_input");
    // TODO Add some actual validation and feedback in the UI
    if (!emailIsValid(emailAddressInput)) {
        console.error("No email address provided");
        return;
    }
    var uploadStatusDiv = document.getElementById("upload_status");
    var uploadFileInput = document.getElementById("file_input");
    var uploadRequest = new XMLHttpRequest();
    if (uploadFileInput.files.length == 0) {
        console.error("No file provided!");
        return;
    }
    var formData = new FormData();
    console.log("Appending file: " + JSON.stringify(uploadFileInput.files[0]));
    formData.append("pdfToConvert", uploadFileInput.files[0]);
    formData.append("emailAddress", emailAddressInput.value);
    formData.append("urlToScan", "www.somesite.com");
    uploadRequest.onreadystatechange = function () {
        if (uploadRequest.readyState == 4) {
            if (uploadRequest.status == 200) {
                uploadStatusDiv.innerText = "File uploaded";
            }
            else {
                uploadStatusDiv.innerText = "Upload failed with status: " + uploadRequest.status + "\n                                             and error: " + uploadRequest.responseText;
            }
        }
    };
    uploadRequest.upload.addEventListener("load", function () {
        uploadStatusDiv.innerText = "File uploaded";
    });
    uploadRequest.upload.addEventListener("error", function (event) {
        uploadStatusDiv.innerText = "File upload failed";
    });
    uploadRequest.upload.addEventListener("abort", function (event) {
        uploadStatusDiv.innerText = "File upload aborted";
    });
    uploadRequest.upload.addEventListener("progress", function (event) {
        if (event.lengthComputable) {
            uploadStatusDiv.innerText = "File upload progress is " + event.loaded / event.total * 100;
        }
    });
    sendRequest(uploadRequest, formData);
}
function startScraping() {
    var uploadRequest = new XMLHttpRequest();
    var scrapingStatusDiv = document.getElementById("scraping_status");
    var formData = new FormData();
    formData.append("emailAddress", "test@email.com");
    formData.append("urlToScan", "www.awesomewebsite.com");
    uploadRequest.onreadystatechange = function () {
        if (uploadRequest.readyState == 4) {
            if (uploadRequest.status == 200) {
                scrapingStatusDiv.innerText = "File uploaded";
            }
            else {
                scrapingStatusDiv.innerText = "Upload failed with status: " + uploadRequest.status + "\n                                             and error: " + uploadRequest.responseText;
            }
        }
    };
    sendRequest(uploadRequest, formData);
}
function sendRequest(req, data) {
    // req.open("POST", "http://vps547804.ovh.net:5000/api/v1/upload");
    req.open("POST", "http://localhost:5000/api/v1/upload");
    req.setRequestHeader("Access-Control-Allow-Origin", "*");
    req.send(data);
}
//# sourceMappingURL=uploader.js.map