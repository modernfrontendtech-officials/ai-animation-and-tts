(function () {
  const form = document.getElementById("job-form");
  const promptField = document.getElementById("prompt");
  const targetLanguageField = document.getElementById("target-language");
  const runtimeMinutesField = document.getElementById("runtime-minutes");
  const filesField = document.getElementById("files");
  const submitButton = document.getElementById("submit-button");
  const errorNode = document.getElementById("form-error");
  const apiBaseUrl = window.APP_CONFIG.apiBaseUrl;

  function formatErrorPayload(payload) {
    if (!payload) {
      return "";
    }
    if (typeof payload === "string") {
      return payload;
    }
    if (payload.detail) {
      if (typeof payload.detail === "string") {
        return payload.detail;
      }
      return JSON.stringify(payload.detail);
    }
    return JSON.stringify(payload);
  }

  async function parseResponse(response) {
    if (!response.ok) {
      const rawText = await response.text();
      let payload = null;
      try {
        payload = rawText ? JSON.parse(rawText) : null;
      } catch (error) {
        payload = rawText;
      }
      const detail = formatErrorPayload(payload);
      throw new Error(
        "Request failed (" +
          response.status +
          " " +
          response.statusText +
          ")" +
          (detail ? ": " + detail : "")
      );
    }
    return response.json();
  }

  function formatNetworkError(error) {
    const message = error instanceof Error ? error.message : String(error || "");
    if (message.includes("Failed to fetch")) {
      return (
        "Cannot reach the backend at " +
        apiBaseUrl +
        ". Check that the backend is running, the browser can access it, and CORS is configured correctly."
      );
    }
    return message || "Failed to create job.";
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
      errorNode.textContent = formatNetworkError(error);
      submitButton.disabled = false;
      submitButton.textContent = "Start Render Job";
    }
  });
})();
