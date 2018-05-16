function uploadFile() {
    var uploadStatusDiv = document.getElementById("uploadStatus");
    var uploadFileInput = document.getElementById("file_input");
    var uploadRequest = new XMLHttpRequest();
    if (uploadFileInput.files.length == 0) {
        console.error("No file provided!");
        return;
    }
    var formData = new FormData();
    console.log("Appending file: " + JSON.stringify(uploadFileInput.files[0]));
    formData.append("pdfToConvert", uploadFileInput.files[0]);
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
    uploadRequest.open("POST", "http://localhost:5000/api/v1/upload");
    uploadRequest.setRequestHeader("Access-Control-Allow-Origin", "*");
    uploadRequest.send(formData);
}
//# sourceMappingURL=uploader.js.map