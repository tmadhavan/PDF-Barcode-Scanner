function emailIsValid(emailAddressInput: HTMLInputElement): boolean {
    console.log("Checking email")
    if (emailAddressInput.value == undefined || emailAddressInput.value == "") {
        return false;
    }

    return true;
}

function uploadFile() {

    let emailAddressInput: HTMLInputElement = document.getElementById("email_input") as HTMLInputElement
    // TODO Add some actual validation and feedback in the UI
    if (!emailIsValid(emailAddressInput)) {
        console.error("No email address provided");
        return;
    }

    let uploadStatusDiv: HTMLDivElement = document.getElementById("upload_status") as HTMLDivElement;
    let uploadFileInput: HTMLInputElement = document.getElementById("file_input") as HTMLInputElement;
    let uploadRequest = new XMLHttpRequest();

    if (uploadFileInput.files.length == 0) {
        console.error("No file provided!");
        return
    }

    let formData = new FormData();

    console.log("Appending file: " + JSON.stringify(uploadFileInput.files[0]));
    formData.append("pdfToConvert", uploadFileInput.files[0]);
    formData.append("emailAddress", emailAddressInput.value);
    formData.append("urlToScan", "www.tmadhavan.com");

    uploadRequest.onreadystatechange = () => {
        if (uploadRequest.readyState == 4) {
            if (uploadRequest.status == 200) {
                uploadStatusDiv.innerText = "File uploaded"
            } else {
                uploadStatusDiv.innerText = `Upload failed with status: ${uploadRequest.status}
                                             and error: ${uploadRequest.responseText}`
            }
        }
    }

    uploadRequest.upload.addEventListener("load", () => {
            uploadStatusDiv.innerText = "File uploaded"
    });

    uploadRequest.upload.addEventListener("error", (event: Event) => {
        uploadStatusDiv.innerText = "File upload failed"
    });

    uploadRequest.upload.addEventListener("abort", (event: Event) => {
        uploadStatusDiv.innerText = "File upload aborted"
    });

    uploadRequest.upload.addEventListener("progress", (event: ProgressEvent) => {
        if (event.lengthComputable) {
            uploadStatusDiv.innerText = `File upload progress is ${event.loaded / event.total * 100}`
        }
    });

    sendRequest(uploadRequest, formData);

}

function startScraping() {
    let uploadRequest = new XMLHttpRequest();
    let scrapingStatusDiv = document.getElementById("scraping_status");

    let formData = new FormData();
    formData.append("emailAddress", "test@email.com");
    formData.append("urlToScan", "www.awesomewebsite.com");

     uploadRequest.onreadystatechange = () => {
        if (uploadRequest.readyState == 4) {
            if (uploadRequest.status == 200) {
                scrapingStatusDiv.innerText = "File uploaded"
            } else {
                scrapingStatusDiv.innerText = `Upload failed with status: ${uploadRequest.status}
                                             and error: ${uploadRequest.responseText}`
            }
        }
    }

    sendRequest(uploadRequest, formData);

}

function sendRequest(req: XMLHttpRequest, data: FormData) {
    req.open("POST", "http://localhost:5000/api/v1/upload");
    req.setRequestHeader("Access-Control-Allow-Origin", "*");
    req.send(data);
}