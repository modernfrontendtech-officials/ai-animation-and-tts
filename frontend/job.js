(function () {
  const params = new URLSearchParams(window.location.search);
  const jobId = params.get("jobId");
  const apiBaseUrl = window.APP_CONFIG.apiBaseUrl;
  const socketUrl = window.APP_CONFIG.socketUrl;
  const socketNamespace = window.APP_CONFIG.socketNamespace;

  const titleNode = document.getElementById("job-title");
  const socketStateNode = document.getElementById("socket-state");
  const statusNode = document.getElementById("job-status");
  const stageNode = document.getElementById("job-stage");
  const progressFillNode = document.getElementById("progress-fill");
  const progressTextNode = document.getElementById("job-progress-text");
  const errorNode = document.getElementById("job-error");
  const eventListNode = document.getElementById("event-list");
  const previewNode = document.getElementById("artifact-preview");
  const scriptNode = document.getElementById("artifact-script");
  const manifestNode = document.getElementById("artifact-manifest");
  const videoNode = document.getElementById("artifact-video");

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

  if (!jobId) {
    titleNode.textContent = "Missing jobId";
    errorNode.hidden = false;
    errorNode.textContent = "No jobId was provided in the URL.";
    return;
  }

  titleNode.textContent = "Job " + jobId;

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
        ". Check that the backend is running and reachable from this browser."
      );
    }
    return message || "Failed to load job.";
  }

  function updateJob(job) {
    const progress = Math.max(0, Math.min(100, Math.round(job.progress || 0)));
    statusNode.textContent = job.status || "loading";
    stageNode.textContent = job.current_stage || "starting";
    progressFillNode.style.width = progress + "%";
    progressTextNode.textContent = progress + "% complete";
    if (job.error_message) {
      errorNode.hidden = false;
      errorNode.textContent = job.error_message;
    }
  }

  function pushEvent(stage, message) {
    const item = document.createElement("li");
    const strong = document.createElement("strong");
    const span = document.createElement("span");
    strong.textContent = stage;
    span.textContent = message;
    item.appendChild(strong);
    item.appendChild(span);
    if (eventListNode.children.length === 1 && eventListNode.textContent.includes("Waiting")) {
      eventListNode.innerHTML = "";
    }
    eventListNode.prepend(item);
    while (eventListNode.children.length > 12) {
      eventListNode.removeChild(eventListNode.lastChild);
    }
  }

  function setArtifactLink(node, label, url) {
    if (!url) {
      node.textContent = "pending";
      return;
    }
    const link = document.createElement("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = label;
    node.innerHTML = "";
    node.appendChild(link);
  }

  async function fetchJob() {
    const response = await fetch(apiBaseUrl + "/api/jobs/" + encodeURIComponent(jobId), {
      cache: "no-store"
    });
    const job = await parseResponse(response);
    updateJob(job);
    if (job.status === "completed") {
      fetchArtifacts().catch(function () {
        return undefined;
      });
    }
  }

  async function fetchArtifacts() {
    const response = await fetch(apiBaseUrl + "/api/jobs/" + encodeURIComponent(jobId) + "/artifacts", {
      cache: "no-store"
    });
    const artifacts = await parseResponse(response);
    setArtifactLink(previewNode, "Open preview", artifacts.preview_page_url);
    setArtifactLink(scriptNode, "Open script manifest", artifacts.script_manifest_url);
    setArtifactLink(manifestNode, "Open assembly manifest", artifacts.job_manifest_url);
    setArtifactLink(videoNode, "Open final video", artifacts.final_video_url);
  }

  fetchJob().catch(function (error) {
    errorNode.hidden = false;
    errorNode.textContent = formatNetworkError(error);
  });

  setInterval(function () {
    fetchJob().catch(function () {
      return undefined;
    });
  }, 5000);

  if (window.io) {
    const socket = window.io(socketUrl + socketNamespace, {
      path: "/socket.io",
      transports: ["websocket", "polling"]
    });

    socket.on("connect", function () {
      socketStateNode.textContent = "connected";
      socket.emit("job:subscribe", { jobId: jobId });
    });

    socket.on("disconnect", function () {
      socketStateNode.textContent = "disconnected";
    });

    socket.on("job:update", function (payload) {
      if (!payload || payload.jobId !== jobId) {
        return;
      }
      updateJob({
        status: payload.status,
        current_stage: payload.stage,
        progress: payload.progress,
        error_message: payload.detail
      });
      pushEvent(payload.stage, payload.message);
      if (payload.status === "completed") {
        fetchArtifacts().catch(function () {
          return undefined;
        });
      }
    });
  } else {
    socketStateNode.textContent = "cdn unavailable";
  }
})();
