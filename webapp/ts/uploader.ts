function uploadFile() {
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
    formData.append("emailAddress", "thomas@tmadhavan.com");


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

    uploadRequest.open("POST", "http://localhost:5000/api/v1/upload");
    uploadRequest.setRequestHeader("Access-Control-Allow-Origin", "*");

    uploadRequest.send(formData)
}