function download_pdf(pdf_data, sFileName) {
	var mediaType = 'application/pdf';
	var textToBLOB = new Blob([pdf_data], { type: mediaType });
    let newLink = document.createElement("a");
    newLink.download = sFileName;

    newLink.href = window.URL.createObjectURL(textToBLOB);
    newLink.style.display = "none";
    document.body.appendChild(newLink);
    newLink.click(); 
}