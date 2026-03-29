(function () {
  const form = document.getElementById("job-form");
  const promptField = document.getElementById("prompt");
  const targetLanguageField = document.getElementById("target-language");
  const runtimeMinutesField = document.getElementById("runtime-minutes");
  const filesField = document.getElementById("files");
  const submitButton = document.getElementById("submit-button");
  const errorNode = document.getElementById("form-error");
  const apiBaseUrl = window.APP_CONFIG.apiBaseUrl;

  async function parseResponse(response) {
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Request failed.");
    }
    return response.json();
  }

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    errorNode.hidden = true;
    submitButton.disabled = true;
    submitButton.textContent = "Queueing job...";

    try {
      const formData = new FormData();
      formData.append("prompt", promptField.value);
      formData.append("target_language", targetLanguageField.value);
      formData.append("runtime_minutes", runtimeMinutesField.value);
      Array.from(filesField.files || []).forEach(function (file) {
        formData.append("files", file);
      });

      const response = await fetch(apiBaseUrl + "/api/jobs", {
        method: "POST",
        body: formData
      });
      const payload = await parseResponse(response);
      window.location.href = "./job.html?jobId=" + encodeURIComponent(payload.job.id);
    } catch (error) {
      errorNode.hidden = false;
      errorNode.textContent = error instanceof Error ? error.message : "Failed to create job.";
      submitButton.disabled = false;
      submitButton.textContent = "Start Render Job";
    }
  });
})();
