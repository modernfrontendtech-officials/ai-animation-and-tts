(function () {
  var isLocalHost =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1";
  var useDedicatedBackendPort = isLocalHost && window.location.port === "3000";
  var backendOrigin = useDedicatedBackendPort
    ? window.location.protocol + "//" + window.location.hostname + ":8000"
    : window.location.origin;

  window.APP_CONFIG = {
    apiBaseUrl: backendOrigin,
    socketUrl: backendOrigin,
    socketNamespace: "/ws"
  };
})();
