document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) {
    alert("Please select a CSV file first.");
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);
  formData.append("text_col", "Comments");  // fixed column name

  document.getElementById("progress").classList.remove("d-none");
  document.getElementById("downloadSection").classList.add("d-none");

  try {
    const response = await fetch("http://127.0.0.1:8000/process_csv", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      alert("Error: " + (error.error || "Unknown error"));
      document.getElementById("progress").classList.add("d-none");
      return;
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    const downloadLink = document.getElementById("downloadLink");
    downloadLink.href = url;

    document.getElementById("progress").classList.add("d-none");
    document.getElementById("downloadSection").classList.remove("d-none");

  } catch (err) {
    alert("Upload failed: " + err.message);
    document.getElementById("progress").classList.add("d-none");
  }
});
