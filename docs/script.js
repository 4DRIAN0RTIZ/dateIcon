(function () {
  var API = "https://dateicon.onrender.com";
  var img = document.getElementById("live-icon");
  var theme = document.getElementById("theme");
  var lang = document.getElementById("lang");
  var dayEl = document.getElementById("day");
  var monthEl = document.getElementById("month");
  var callPath = document.getElementById("call-path");
  var wake = document.getElementById("wake");
  var wakeMsg = document.getElementById("wake-msg");

  var MESSAGES = [
    "Waking the API…",
    "Render free tier is stretching…",
    "Cold start: the dyno was napping.",
    "Pinging /health until it answers.",
    "Still cheaper than keeping it warm.",
    "Almost — PNG stamps incoming."
  ];

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function clampDate() {
    var d = parseInt(dayEl.value, 10);
    var m = parseInt(monthEl.value, 10);
    if (isNaN(d) || d < 1) d = 1;
    if (d > 31) d = 31;
    if (isNaN(m) || m < 1) m = 1;
    if (m > 12) m = 12;
    dayEl.value = d;
    monthEl.value = m;
    return { dd: pad(d), mm: pad(m), d: d, m: m };
  }

  function iconPath() {
    var p = clampDate();
    return "/icon/" + p.dd + "_" + p.mm;
  }

  function src() {
    return API + iconPath() + "?theme=" + theme.value + "&lang=" + lang.value + "&size=256";
  }

  function updateCall() {
    var p = clampDate();
    callPath.textContent = "GET /icon/" + p.dd + "_" + p.mm;
  }

  function loadIcon() {
    img.src = src();
  }

  function cycleMessages() {
    var i = 0;
    wakeMsg.textContent = MESSAGES[0];
    return setInterval(function () {
      i = (i + 1) % MESSAGES.length;
      wakeMsg.style.opacity = "0";
      setTimeout(function () {
        wakeMsg.textContent = MESSAGES[i];
        wakeMsg.style.opacity = "1";
      }, 220);
    }, 2800);
  }

  function pingHealth() {
    return fetch(API + "/health", { cache: "no-store", mode: "cors" })
      .then(function (r) { return r.ok; })
      .catch(function () { return false; });
  }

  function pingIcon() {
    return new Promise(function (resolve) {
      var probe = new Image();
      var done = false;
      var t = setTimeout(function () {
        if (done) return;
        done = true;
        probe.onload = probe.onerror = null;
        resolve(false);
      }, 8000);
      probe.onload = function () {
        if (done) return;
        done = true;
        clearTimeout(t);
        resolve(true);
      };
      probe.onerror = function () {
        if (done) return;
        done = true;
        clearTimeout(t);
        resolve(false);
      };
      probe.src = API + iconPath() + "?theme=default&size=64&_=" + Date.now();
    });
  }

  function waitForServer() {
    wake.hidden = false;
    var ticker = cycleMessages();
    var deadline = Date.now() + 90000;

    function finish(ok) {
      clearInterval(ticker);
      wake.hidden = true;
      if (ok) loadIcon();
    }

    function loop() {
      return pingHealth().then(function (ok) {
        if (ok) {
          finish(true);
          return;
        }
        return pingIcon().then(function (iconOk) {
          if (iconOk) {
            finish(true);
            return;
          }
          if (Date.now() > deadline) {
            wakeMsg.textContent = "API still asleep.";
            setTimeout(function () { finish(false); }, 1600);
            return;
          }
          return new Promise(function (res) { setTimeout(res, 2500); }).then(loop);
        });
      });
    }

    return loop();
  }

  function onDial() {
    updateCall();
    loadIcon();
  }
  theme.addEventListener("change", onDial);
  lang.addEventListener("change", onDial);
  dayEl.addEventListener("change", onDial);
  monthEl.addEventListener("change", onDial);
  dayEl.addEventListener("input", updateCall);
  monthEl.addEventListener("input", updateCall);

  (function seedToday() {
    var now = new Date();
    dayEl.value = now.getDate();
    monthEl.value = now.getMonth() + 1;
    updateCall();
  })();
  waitForServer();

  function fill(id, file, title) {
    fetch(file)
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.items || !data.items.length) return;
        var el = document.getElementById(id);
        var h = document.createElement("h2");
        h.textContent = title;
        var ul = document.createElement("ul");
        data.items.forEach(function (item) {
          var li = document.createElement("li");
          li.textContent = typeof item === "string" ? item : (item.title || JSON.stringify(item));
          ul.appendChild(li);
        });
        el.appendChild(h);
        el.appendChild(ul);
        el.hidden = false;
      })
      .catch(function () {});
  }

  fill("roadmap", "roadmap.json", "Roadmap");
  fill("changelog", "changelog.json", "Changelog");
})();
