class Uploader {

  statusDiv: HTMLDivElement;
  emailInput: HTMLInputElement;
  uploadFileInput: HTMLInputElement;

  constructor() {
    this.statusDiv = document.getElementById("status") as HTMLDivElement;
    this.emailInput = document.getElementById("email_input") as HTMLInputElement;
    this.uploadFileInput = document.getElementById("file_input") as HTMLInputElement;
  }

  emailIsValid(): boolean {
    console.log("Checking email");
    return !(this.emailInput.value == undefined || this.emailInput.value == "");
  }

  uploadFile() {

    this.clearStatus();

    // TODO Add some actual validation
    if (!this.emailIsValid()) {
      console.error("No email address provided");
      this.status("Please provide an email address", true);
      return;
    }

    let uploadRequest = new XMLHttpRequest();

    if (this.uploadFileInput.files.length == 0) {
      console.error("No file provided!");
      this.status("Please provide a PDF file to scan");
      return
    }

    let formData = new FormData();

    console.log("Appending file: " + JSON.stringify(this.uploadFileInput.files[0]));
    formData.append("pdfToConvert", this.uploadFileInput.files[0]);
    formData.append("emailAddress", this.emailInput.value);
    formData.append("urlToScan", "www.somesite.com");

    uploadRequest.onreadystatechange = () => {
      if (uploadRequest.readyState == 4) {
        if (uploadRequest.status == 200) {
          this.status("File uploaded");
        } else {
          this.status(`Upload failed with status: ${uploadRequest.status}
                                             and error: ${uploadRequest.responseText}`)
        }
      }
    };

    uploadRequest.upload.addEventListener("load", () => {
      this.status("File uploaded");
    });

    uploadRequest.upload.addEventListener("error", (event: Event) => {
      this.status("File upload failed");
    });

    uploadRequest.upload.addEventListener("abort", (event: Event) => {
      this.status("File upload aborted");
    });

    uploadRequest.upload.addEventListener("progress", (event: ProgressEvent) => {
      if (event.lengthComputable) {
        this.status(`File upload progress is ${event.loaded / event.total * 100}`);
      }
    });

    this.sendRequest(uploadRequest, formData);

  }

  clearStatus() {
    this.status("", false, true);
    this.statusDiv.hidden = true;
  }

  status(statusMessage: string, isError: boolean = false, hidden?: boolean) {

    if (isError) {
      this.statusDiv.classList.add("alert-danger");
      this.statusDiv.classList.remove("alert-info");
    } else {
      this.statusDiv.classList.add("alert-info");
      this.statusDiv.classList.remove("alert-danger");
    }
    this.statusDiv.innerText = statusMessage;

    if (hidden) {
      this.statusDiv.hidden = hidden;
    } else {
      this.statusDiv.hidden = false;
    }
  }

  startScraping() {
    // TODO This is going to be a bit more work than first thought :-D
  }

  sendRequest(req: XMLHttpRequest, data: FormData) {
    // req.open("POST", "http://vps547804.ovh.net:5000/api/v1/upload");
    req.open("POST", "http://localhost:5000/api/v1/upload");
    req.setRequestHeader("Access-Control-Allow-Origin", "*");
    req.send(data);
  }
}

