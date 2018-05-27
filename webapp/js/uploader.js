var Uploader = /** @class */ (function () {
    function Uploader() {
        this.statusDiv = document.getElementById("status");
        this.emailInput = document.getElementById("email_input");
        this.uploadFileInput = document.getElementById("file_input");
    }
    Uploader.prototype.emailIsValid = function () {
        console.log("Checking email");
        return !(this.emailInput.value == undefined || this.emailInput.value == "");
    };
    Uploader.prototype.uploadFile = function () {
        var _this = this;
        this.clearStatus();
        // TODO Add some actual validation
        if (!this.emailIsValid()) {
            console.error("No email address provided");
            this.status("Please provide an email address");
            return;
        }
        var uploadRequest = new XMLHttpRequest();
        if (this.uploadFileInput.files.length == 0) {
            console.error("No file provided!");
            this.status("Please provide a PDF file to scan");
            return;
        }
        var formData = new FormData();
        console.log("Appending file: " + JSON.stringify(this.uploadFileInput.files[0]));
        formData.append("pdfToConvert", this.uploadFileInput.files[0]);
        formData.append("emailAddress", this.emailInput.value);
        formData.append("urlToScan", "www.somesite.com");
        uploadRequest.onreadystatechange = function () {
            if (uploadRequest.readyState == 4) {
                if (uploadRequest.status == 200) {
                    _this.status("File uploaded");
                }
                else {
                    _this.status("Upload failed with status: " + uploadRequest.status + "\n                                             and error: " + uploadRequest.responseText);
                }
            }
        };
        uploadRequest.upload.addEventListener("load", function () {
            _this.status("File uploaded");
        });
        uploadRequest.upload.addEventListener("error", function (event) {
            _this.status("File upload failed", true);
        });
        uploadRequest.upload.addEventListener("abort", function (event) {
            _this.status("File upload aborted", true);
        });
        uploadRequest.upload.addEventListener("progress", function (event) {
            if (event.lengthComputable) {
                _this.status("File upload progress is " + event.loaded / event.total * 100);
            }
        });
        this.sendRequest(uploadRequest, formData);
    };
    Uploader.prototype.clearStatus = function () {
        this.status("", false, true);
        this.statusDiv.hidden = true;
    };
    Uploader.prototype.status = function (statusMessage, isError, hidden) {
        if (isError === void 0) { isError = false; }
        if (isError) {
            this.statusDiv.classList.add("alert-danger");
            this.statusDiv.classList.remove("alert-info");
        }
        else {
            this.statusDiv.classList.add("alert-info");
            this.statusDiv.classList.remove("alert-danger");
        }
        this.statusDiv.innerText = statusMessage;
        if (hidden) {
            this.statusDiv.hidden = hidden;
        }
        else {
            this.statusDiv.hidden = false;
        }
    };
    Uploader.prototype.startScraping = function () {
        // TODO This is going to be a bit more work than first thought :-D
    };
    Uploader.prototype.sendRequest = function (req, data) {
        var _this = this;
        req.addEventListener("timeout", function (event) {
            _this.status("Request timed out", true);
        });
        req.open("POST", "http://vps547804.ovh.net/api/v1/upload");
        req.timeout = 5000;
        req.setRequestHeader("Access-Control-Allow-Origin", "*");
        req.send(data);
    };
    return Uploader;
}());
//# sourceMappingURL=uploader.js.map