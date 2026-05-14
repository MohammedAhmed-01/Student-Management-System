/**
 * Student Management System — static frontend (HTML/CSS/JS only)
 * Backend base URL and routes verified against FastAPI app.
 */

const API_BASE = "http://localhost:8000";

/** Pagination: backend uses `skip` + `limit` (limit max 100). */
let studentPageIndex = 0;
let deleteTargetId = null;
let currentUser = null;
/** @type {Record<number, string>} */
let userEmailById = {};

// ----- DOM helpers -----
function $(id) {
  return document.getElementById(id);
}

function showEl(el) {
  if (el) el.classList.remove("hidden");
}

function hideEl(el) {
  if (el) el.classList.add("hidden");
}

// ----- Token storage (localStorage) -----
function getToken() {
  return localStorage.getItem("access_token") || localStorage.getItem("token");
}

function setToken(accessToken, tokenType) {
  if (accessToken) localStorage.setItem("access_token", accessToken);
  else localStorage.removeItem("access_token");
  if (tokenType) localStorage.setItem("token_type", tokenType);
  else localStorage.removeItem("token_type");
  localStorage.removeItem("token");
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_type");
  localStorage.removeItem("token");
  currentUser = null;
  userEmailById = {};
  showAuthLayout();
  showSection("login");
  clearAlert("alert-login");
  clearAlert("alert-register");
}

/**
 * GET /users/me — returns the same shape as {@link apiRequest}.
 */
async function loadCurrentUser() {
  return await apiRequest("/users/me");
}

function requireAuth() {
  return !!getToken();
}

// ----- Messaging -----
/**
 * Show a reusable alert. Pass element id (string) or HTMLElement.
 * @param {"success"|"error"|"warning"} type
 */
function showMessage(type, message, target) {
  var el =
    typeof target === "string"
      ? $(target)
      : target || $("global-alert");
  if (!el) return;
  el.textContent = message;
  el.classList.remove("hidden", "alert--success", "alert--error", "alert--warning");
  if (type === "success") el.classList.add("alert--success");
  else if (type === "warning") el.classList.add("alert--warning");
  else el.classList.add("alert--error");
  showEl(el);
}

function clearAlert(target) {
  var el = typeof target === "string" ? $(target) : target;
  if (!el) return;
  el.textContent = "";
  el.classList.add("hidden");
  el.classList.remove("alert--success", "alert--error", "alert--warning");
}

function formatApiError(data) {
  if (!data) return "Request failed.";
  if (typeof data.message === "string" && data.detail) {
    var inner = formatApiError({ detail: data.detail });
    return data.message + " " + inner;
  }
  var d = data.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map(function (x) {
        if (x && typeof x.msg === "string") return x.msg;
        return JSON.stringify(x);
      })
      .join(" ");
  }
  if (data.detail && typeof data.detail === "object") {
    try {
      return JSON.stringify(data.detail);
    } catch (e) {
      return "Request failed.";
    }
  }
  return "Request failed.";
}

/**
 * Fetch helper — attaches JSON + Bearer token.
 * @param {string} endpoint path beginning with /
 * @param {{ method?: string, body?: object, skipAuthRedirect?: boolean }} options
 */
async function apiRequest(endpoint, options) {
  options = options || {};
  var method = options.method || "GET";
  var headers = { "Content-Type": "application/json" };
  var token = getToken();
  if (token) {
    headers.Authorization = "Bearer " + token;
  }
  var init = { method: method, headers: headers };
  if (options.body !== undefined) {
    init.body = JSON.stringify(options.body);
  }
  var res;
  try {
    res = await fetch(API_BASE + endpoint, init);
  } catch (err) {
    return {
      ok: false,
      status: 0,
      data: {
        detail:
          "Cannot reach the API at " +
          API_BASE +
          ". Is the backend running, and is CORS allowing this page's origin?",
      },
    };
  }
  var text = await res.text();
  var data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch (e) {
      data = { detail: text };
    }
  }
  if (res.status === 401 && !options.skipAuthRedirect) {
    setToken(null, null);
    currentUser = null;
    showAuthLayout();
    showSection("login");
    showMessage("error", "Session expired, please login again.", "alert-login");
  }
  return { ok: res.ok, status: res.status, data: data };
}

// ----- Layout / sections -----
function showAuthLayout() {
  showEl($("view-auth"));
  hideEl($("view-app"));
  var sb = $("sidebar");
  if (sb) sb.classList.remove("is-open");
}

function showAppLayout() {
  hideEl($("view-auth"));
  showEl($("view-app"));
}

/**
 * Auth: "login" | "register". App: "dashboard" | "students" | "profile" | "monitoring"
 */
function showSection(name) {
  if (name === "login") {
    showAuthLayout();
    showEl($("section-login"));
    hideEl($("section-register"));
    return;
  }
  if (name === "register") {
    showAuthLayout();
    hideEl($("section-login"));
    showEl($("section-register"));
    return;
  }
  showAppLayout();
  document.querySelectorAll(".nav-item").forEach(function (btn) {
    var sec = btn.getAttribute("data-section");
    btn.classList.toggle("is-active", sec === name);
  });
  document.querySelectorAll(".page-section").forEach(function (sec) {
    sec.classList.add("hidden");
  });
  var page = $("page-" + name);
  if (page) page.classList.remove("hidden");
  var titles = {
    dashboard: ["Dashboard", "Overview for your role"],
    students: ["Students", "Directory, filters, and CRUD (admin)"],
    profile: ["Profile", "Your account and linked student record"],
    monitoring: ["Monitoring", "Operational metrics from the API"],
  };
  var t = titles[name] || ["", ""];
  $("page-title").textContent = t[0];
  $("page-subtitle").textContent = t[1];
  clearAlert("global-alert");
}

function setAdminNavVisible(isAdmin) {
  $("nav-students").classList.toggle("hidden", !isAdmin);
  $("nav-monitoring").classList.toggle("hidden", !isAdmin);
}

async function refreshUserEmailMap() {
  userEmailById = {};
  if (!currentUser || currentUser.role !== "admin") return;
  var res = await apiRequest("/users/");
  if (!res.ok || !Array.isArray(res.data)) return;
  res.data.forEach(function (u) {
    userEmailById[u.id] = u.email || "";
  });
}

async function enterApp() {
  if (!requireAuth()) {
    showSection("login");
    return;
  }
  showAppLayout();
  var me = await loadCurrentUser();
  if (!me.ok) {
    if (me.status === 401) {
      return;
    }
    setToken(null, null);
    currentUser = null;
    showAuthLayout();
    showSection("login");
    showMessage("error", formatApiError(me.data), "alert-login");
    return;
  }
  currentUser = me.data;
  showSection("dashboard");
  var pill =
    (currentUser.full_name || currentUser.email || "") +
    " · " +
    (currentUser.role || "");
  $("user-pill").textContent = pill;

  var isAdmin = currentUser.role === "admin";
  setAdminNavVisible(isAdmin);
  $("dashboard-admin").classList.toggle("hidden", !isAdmin);
  $("dashboard-student").classList.toggle("hidden", isAdmin);

  if (!isAdmin) {
    var welcome = $("dashboard-student-welcome");
    if (welcome) {
      welcome.textContent =
        "Signed in as " + (currentUser.full_name || currentUser.email) + ".";
    }
  }

  $("dashboard-monitoring-preview").classList.toggle("hidden", !isAdmin);
  if (isAdmin) {
    studentPageIndex = 0;
    await refreshUserEmailMap();
    await loadDashboardAdminStats();
    await loadDashboardMonitoringPreview();
  } else {
    hideEl($("dashboard-monitoring-preview"));
  }
  await refreshDashboardCommon();
}

async function loadDashboardAdminStats() {
  var box = $("dashboard-stat-cards");
  if (!box) return;
  box.innerHTML = "";
  clearAlert("alert-dashboard");
  var res = await apiRequest("/students/stats/summary");
  if (!res.ok) {
    showMessage("error", "Statistics: " + formatApiError(res.data), "alert-dashboard");
    return;
  }
  var d = res.data;
  function card(label, value, hint) {
    var div = document.createElement("div");
    div.className = "stat-card";
    div.innerHTML =
      '<div class="stat-card__label">' +
      escapeHtml(label) +
      '</div><div class="stat-card__value">' +
      escapeHtml(String(value)) +
      "</div>" +
      (hint
        ? '<div class="stat-card__hint">' + escapeHtml(hint) + "</div>"
        : "");
    box.appendChild(div);
  }
  card("Total students", d.total_students != null ? d.total_students : "—", null);
  card("Average GPA", d.average_gpa != null ? d.average_gpa : "—", null);
  var deptCount =
    d.departments && typeof d.departments === "object"
      ? Object.keys(d.departments).length
      : 0;
  card("Departments", deptCount, "Distinct department values in the database.");
  var active =
    d.statuses && typeof d.statuses === "object" && d.statuses.active != null
      ? d.statuses.active
      : null;
  card("Active (status)", active != null ? active : "—", "Count where status is 'active'.");
}

async function loadDashboardMonitoringPreview() {
  var wrap = $("dashboard-monitoring-preview");
  var chips = $("dashboard-metrics-chips");
  if (!wrap || !chips) return;
  var m = await apiRequest("/monitoring/metrics");
  chips.innerHTML = "";
  if (!m.ok) {
    chips.innerHTML =
      "<p class=\"text-muted text-sm\">" + escapeHtml(formatApiError(m.data)) + "</p>";
    showEl(wrap);
    return;
  }
  function chip(label, val) {
    var div = document.createElement("div");
    div.className = "metric-chip";
    div.innerHTML = "<span>" + escapeHtml(label) + "</span><strong>" + escapeHtml(val) + "</strong>";
    chips.appendChild(div);
  }
  chip("Total requests", String(m.data.total_requests ?? "—"));
  chip("Errors", String(m.data.total_errors ?? "—"));
  chip("Health", String(m.data.system_health ?? "—"));
  showEl(wrap);
}

async function refreshDashboardCommon() {
  clearAlert("alert-monitoring");
  var pre = $("metrics-json");
  var summary = $("metrics-summary");
  if (pre) pre.textContent = "Loading…";
  if (summary) summary.innerHTML = "";

  var isAdmin = currentUser && currentUser.role === "admin";
  if (!isAdmin) {
    if (pre) pre.textContent = "Monitoring is available to administrators.";
    return;
  }

  var m = await apiRequest("/monitoring/metrics");
  if (!m.ok) {
    if (pre) pre.textContent = "Error: " + formatApiError(m.data);
    return;
  }
  if (pre) pre.textContent = JSON.stringify(m.data, null, 2);
  if (summary && m.data) {
    summary.innerHTML = "";
    function chip(label, val) {
      var div = document.createElement("div");
      div.className = "metric-chip";
      div.innerHTML = "<span>" + escapeHtml(label) + "</span><strong>" + escapeHtml(val) + "</strong>";
      summary.appendChild(div);
    }
    chip("Total requests", String(m.data.total_requests ?? "—"));
    chip("Total errors", String(m.data.total_errors ?? "—"));
    chip("Error rate", String(m.data.overall_error_rate ?? "—") + "%");
    chip("Health", String(m.data.system_health ?? "—"));
  }
}

function getPageSize() {
  var sel = $("page-size");
  var n = parseInt(sel && sel.value ? sel.value : "10", 10);
  if (isNaN(n) || n < 1) return 10;
  if (n > 100) return 100;
  return n;
}

function buildStudentsQuery() {
  var params = new URLSearchParams();
  var search = $("filter-search").value.trim();
  var dept = $("filter-department").value.trim();
  var status = $("filter-status").value.trim();
  var gmin = $("filter-gpa-min").value;
  var gmax = $("filter-gpa-max").value;
  if (search) params.set("search", search);
  if (dept) params.set("department", dept);
  if (status) params.set("status", status);
  if (gmin !== "") params.set("gpa_min", gmin);
  if (gmax !== "") params.set("gpa_max", gmax);
  var limit = getPageSize();
  params.set("skip", String(studentPageIndex * limit));
  params.set("limit", String(limit));
  return params.toString();
}

async function loadStudentsTable() {
  if (!currentUser || currentUser.role !== "admin") return;
  clearAlert("alert-students");
  var tbody = $("tbody-students");
  var loading = $("students-loading");
  if (loading) loading.textContent = "Loading…";
  tbody.innerHTML =
    '<tr><td colspan="8" class="text-muted">Loading…</td></tr>';

  var res = await apiRequest("/students/?" + buildStudentsQuery());
  tbody.innerHTML = "";
  if (loading) loading.textContent = "";

  if (!res.ok) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-muted">—</td></tr>';
    showMessage("error", formatApiError(res.data), "alert-students");
    return;
  }
  var rows = Array.isArray(res.data) ? res.data : [];
  if (rows.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="8" class="text-muted">No students found for this page or filters.</td></tr>';
  } else {
    rows.forEach(function (stu) {
      var email = userEmailById[stu.user_id] || "—";
      var tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" +
        stu.id +
        "</td><td>" +
        escapeHtml(stu.university_id) +
        "</td><td>" +
        escapeHtml(stu.name) +
        "</td><td>" +
        escapeHtml(email) +
        "</td><td>" +
        escapeHtml(stu.department) +
        "</td><td>" +
        (stu.gpa != null ? Number(stu.gpa).toFixed(2) : "") +
        "</td><td>" +
        escapeHtml(stu.status) +
        '</td><td><div class="table-actions">' +
        '<button type="button" class="btn btn--ghost btn--sm btn-view" data-id="' +
        stu.id +
        '">View</button>' +
        '<button type="button" class="btn btn--secondary btn--sm btn-edit" data-id="' +
        stu.id +
        '">Edit</button>' +
        '<button type="button" class="btn btn--danger btn--sm btn-del" data-id="' +
        stu.id +
        '" data-name="' +
        escapeHtml(stu.name) +
        '">Delete</button></div></td>';
      tbody.appendChild(tr);
    });
  }

  $("page-label").textContent = "Page " + (studentPageIndex + 1);
  $("btn-page-prev").disabled = studentPageIndex === 0;
  var limit = getPageSize();
  $("btn-page-next").disabled = rows.length < limit;
}

function escapeHtml(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function populateUserSelect() {
  var sel = $("field-user-id");
  sel.innerHTML = "";
  await refreshUserEmailMap();
  var res = await apiRequest("/users/");
  if (!res.ok || !Array.isArray(res.data)) {
    var o = document.createElement("option");
    o.value = "";
    o.textContent = "Could not load users (" + formatApiError(res.data) + ")";
    sel.appendChild(o);
    return;
  }
  var placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select user…";
  sel.appendChild(placeholder);
  res.data.forEach(function (u) {
    var opt = document.createElement("option");
    opt.value = String(u.id);
    opt.textContent = "#" + u.id + " · " + (u.email || "") + " · " + (u.role || "");
    sel.appendChild(opt);
  });
}

function openStudentModal(isEdit, studentId) {
  clearAlert("alert-modal-student");
  $("form-student").reset();
  $("field-edit-id").value = isEdit ? String(studentId) : "";
  $("modal-student-title").textContent = isEdit ? "Edit student" : "Add student";
  var sel = $("field-user-id");
  sel.disabled = !!isEdit;

  if (!isEdit) {
    $("field-enrollment").value = new Date().toISOString().slice(0, 10);
    $("field-gpa").value = "0";
    populateUserSelect();
  } else {
    apiRequest("/students/" + studentId).then(function (res) {
      if (!res.ok) {
        showMessage("error", formatApiError(res.data), "alert-modal-student");
        return;
      }
      var s = res.data;
      sel.innerHTML = "";
      var opt = document.createElement("option");
      opt.value = String(s.user_id);
      opt.textContent =
        "#" + s.user_id + " · " + (userEmailById[s.user_id] || "user") + " (locked)";
      opt.selected = true;
      sel.appendChild(opt);
      $("field-university-id").value = s.university_id || "";
      $("field-name").value = s.name || "";
      $("field-department").value = s.department || "";
      $("field-enrollment").value = (s.enrollment_date || "").slice(0, 10);
      $("field-gpa").value = s.gpa != null ? String(s.gpa) : "0";
      $("field-status").value = s.status || "active";
      $("field-gender").value = s.gender || "";
      $("field-phone").value = s.phone_number || "";
      $("field-birth").value = (s.birth_date || "").slice(0, 10);
    });
  }
  showEl($("modal-student"));
}

function closeModals() {
  hideEl($("modal-student"));
  hideEl($("modal-delete"));
  hideEl($("modal-view-student"));
}

function validateGpaField() {
  var raw = $("field-gpa").value;
  var g = parseFloat(raw);
  if (raw === "" || isNaN(g)) return "GPA must be a number.";
  if (g < 0 || g > 4) return "GPA must be between 0 and 4.";
  return null;
}

async function saveStudent(ev) {
  ev.preventDefault();
  clearAlert("alert-modal-student");
  var editId = $("field-edit-id").value.trim();

  var gpaErr = validateGpaField();
  if (gpaErr) {
    showMessage("error", gpaErr, "alert-modal-student");
    return;
  }

  var payload = {
    university_id: $("field-university-id").value.trim(),
    name: $("field-name").value.trim(),
    department: $("field-department").value.trim(),
    enrollment_date: $("field-enrollment").value,
    gpa: parseFloat($("field-gpa").value),
    status: $("field-status").value,
  };
  var g = $("field-gender").value.trim();
  payload.gender = g || null;
  var ph = $("field-phone").value.trim();
  payload.phone_number = ph || null;
  var bd = $("field-birth").value;
  payload.birth_date = bd || null;

  if (!payload.university_id || !payload.name || !payload.department || !payload.enrollment_date) {
    showMessage("error", "Please fill all required fields.", "alert-modal-student");
    return;
  }

  if (!editId) {
    var uid = parseInt($("field-user-id").value, 10);
    if (!uid) {
      showMessage("error", "User ID is required.", "alert-modal-student");
      return;
    }
    payload.user_id = uid;
    var res = await apiRequest("/students/", { method: "POST", body: payload });
    if (!res.ok) {
      showMessage("error", formatApiError(res.data), "alert-modal-student");
      return;
    }
    closeModals();
    showMessage("success", "Student created.", "alert-students");
    await loadStudentsTable();
    await loadDashboardAdminStats();
    return;
  }

  delete payload.user_id;
  var resPatch = await apiRequest("/students/" + editId, {
    method: "PATCH",
    body: payload,
  });
  if (!resPatch.ok) {
    showMessage("error", formatApiError(resPatch.data), "alert-modal-student");
    return;
  }
  closeModals();
  showMessage("success", "Student updated.", "alert-students");
  await loadStudentsTable();
  await loadDashboardAdminStats();
}

function confirmDeleteStudent(id, name) {
  deleteTargetId = id;
  $("delete-student-text").textContent =
    'This will permanently remove "' + name + '" (id ' + id + ").";
  showEl($("modal-delete"));
}

async function doDeleteStudent() {
  if (deleteTargetId == null) return;
  var res = await apiRequest("/students/" + deleteTargetId, { method: "DELETE" });
  if (!res.ok) {
    showMessage("error", formatApiError(res.data), "alert-students");
    return;
  }
  deleteTargetId = null;
  closeModals();
  showMessage("success", "Student deleted.", "alert-students");
  await loadStudentsTable();
  await loadDashboardAdminStats();
}

async function openViewStudent(id) {
  var res = await apiRequest("/students/" + id);
  var body = $("view-student-body");
  body.innerHTML = "";
  if (!res.ok) {
    body.innerHTML =
      "<p class=\"text-muted\">" + escapeHtml(formatApiError(res.data)) + "</p>";
    showEl($("modal-view-student"));
    return;
  }
  var s = res.data;
  var email = userEmailById[s.user_id] || "—";
  function row(label, val) {
    return (
      '<div class="detail-row"><dt>' +
      escapeHtml(label) +
      "</dt><dd>" +
      escapeHtml(val) +
      "</dd></div>"
    );
  }
  body.innerHTML =
    row("ID", String(s.id)) +
    row("User ID", String(s.user_id)) +
    row("User email", email) +
    row("University ID", s.university_id) +
    row("Name", s.name) +
    row("Department", s.department) +
    row("GPA", s.gpa != null ? String(s.gpa) : "—") +
    row("Status", s.status) +
    row("Enrollment", s.enrollment_date || "—") +
    row("Birth date", s.birth_date || "—") +
    row("Gender", s.gender || "—") +
    row("Phone", s.phone_number || "—");
  showEl($("modal-view-student"));
}

async function loadProfile() {
  clearAlert("alert-profile");
  var u = await apiRequest("/users/me");
  if (!u.ok) {
    showMessage("error", formatApiError(u.data), "alert-profile");
    return;
  }
  var user = u.data;
  $("card-profile-user").innerHTML =
    "<h3 class=\"card__title card__title--sm\">Account</h3>" +
    "<p><strong>Email:</strong> " +
    escapeHtml(user.email) +
    "</p>" +
    "<p><strong>Full name:</strong> " +
    escapeHtml(user.full_name || "—") +
    "</p>" +
    "<p><strong>Role:</strong> " +
    escapeHtml(user.role) +
    "</p>" +
    "<p><strong>User ID:</strong> " +
    user.id +
    "</p>";

  var stCard = $("card-profile-student");
  if (user.role !== "student") {
    stCard.classList.add("hidden");
    return;
  }
  stCard.classList.remove("hidden");
  var st = await apiRequest("/students/me");
  if (st.status === 404 || !st.ok) {
    stCard.innerHTML =
      "<h3 class=\"card__title card__title--sm\">Student record</h3>" +
      "<p class=\"text-muted text-sm\">No linked student row yet (<code class=\"code-inline\">GET /students/me</code>).</p>";
    return;
  }
  var s = st.data;
  stCard.innerHTML =
    "<h3 class=\"card__title card__title--sm\">Student record</h3>" +
    "<p><strong>University ID:</strong> " +
    escapeHtml(s.university_id) +
    "</p>" +
    "<p><strong>Department:</strong> " +
    escapeHtml(s.department) +
    "</p>" +
    "<p><strong>GPA:</strong> " +
    escapeHtml(String(s.gpa)) +
    "</p>" +
    "<p><strong>Status:</strong> " +
    escapeHtml(s.status) +
    "</p>";
}

function onNavigate(section) {
  if (!currentUser) return;
  if (section !== "dashboard" && section !== "profile") {
    if (currentUser.role !== "admin") return;
  }
  showSection(section);
  if (section === "dashboard") {
    if (currentUser.role === "admin") {
      loadDashboardAdminStats();
      loadDashboardMonitoringPreview();
    }
    refreshDashboardCommon();
  }
  if (section === "students") loadStudentsTable();
  if (section === "profile") loadProfile();
  if (section === "monitoring") refreshDashboardCommon();
}

// ----- Boot -----
document.addEventListener("DOMContentLoaded", function () {
  $("btn-goto-register").addEventListener("click", function () {
    clearAlert("alert-register");
    showSection("register");
  });
  $("btn-goto-login").addEventListener("click", function () {
    clearAlert("alert-login");
    showSection("login");
  });

  $("form-login").addEventListener("submit", async function (ev) {
    ev.preventDefault();
    clearAlert("alert-login");
    var email = $("login-email").value.trim();
    var password = $("login-password").value;
    if (!email || !password) {
      showMessage("error", "Email and password are required.", "alert-login");
      return;
    }
    var res = await apiRequest("/auth/login", {
      method: "POST",
      body: { email: email, password: password },
      skipAuthRedirect: true,
    });
    if (!res.ok) {
      showMessage("error", formatApiError(res.data), "alert-login");
      return;
    }
    setToken(res.data.access_token, res.data.token_type || "bearer");
    await enterApp();
  });

  $("form-register").addEventListener("submit", async function (ev) {
    ev.preventDefault();
    clearAlert("alert-register");
    var full = $("reg-full-name").value.trim();
    var email = $("reg-email").value.trim();
    var password = $("reg-password").value;
    var role = $("reg-role").value;
    if (!full || !email || !password) {
      showMessage("error", "All fields are required.", "alert-register");
      return;
    }
    if (role !== "admin" && role !== "student") {
      showMessage("error", "Role must be admin or student.", "alert-register");
      return;
    }
    if (role === "admin") {
      showMessage(
        "warning",
        "Public registration cannot create admin users on this API. Ask an administrator to create your account with POST /users/, or choose Student.",
        "alert-register"
      );
      return;
    }
    var res = await apiRequest("/auth/register", {
      method: "POST",
      body: {
        email: email,
        password: password,
        full_name: full,
        role: "student",
      },
      skipAuthRedirect: true,
    });
    if (!res.ok) {
      showMessage("error", formatApiError(res.data), "alert-register");
      return;
    }
    showMessage("success", "Account created. You can sign in now.", "alert-register");
    setTimeout(function () {
      showSection("login");
    }, 800);
  });

  $("btn-logout").addEventListener("click", logout);

  document.querySelectorAll(".nav-item").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var sec = btn.getAttribute("data-section");
      if (sec) onNavigate(sec);
      var sb = $("sidebar");
      if (sb) sb.classList.remove("is-open");
    });
  });

  $("btn-sidebar-toggle").addEventListener("click", function () {
    $("sidebar").classList.toggle("is-open");
  });

  var btnMon = $("btn-goto-monitoring");
  if (btnMon) {
    btnMon.addEventListener("click", function () {
      onNavigate("monitoring");
      $("sidebar").classList.remove("is-open");
    });
  }

  $("btn-add-student").addEventListener("click", function () {
    openStudentModal(false, null);
  });
  $("form-student").addEventListener("submit", saveStudent);
  $("btn-apply-filters").addEventListener("click", function () {
    studentPageIndex = 0;
    loadStudentsTable();
  });
  $("btn-reset-filters").addEventListener("click", function () {
    $("filter-search").value = "";
    $("filter-department").value = "";
    $("filter-status").value = "";
    $("filter-gpa-min").value = "";
    $("filter-gpa-max").value = "";
    studentPageIndex = 0;
    loadStudentsTable();
  });
  $("page-size").addEventListener("change", function () {
    studentPageIndex = 0;
    loadStudentsTable();
  });
  $("btn-page-prev").addEventListener("click", function () {
    if (studentPageIndex > 0) {
      studentPageIndex--;
      loadStudentsTable();
    }
  });
  $("btn-page-next").addEventListener("click", function () {
    studentPageIndex++;
    loadStudentsTable();
  });

  $("tbody-students").addEventListener("click", function (ev) {
    var viewBtn = ev.target.closest(".btn-view");
    if (viewBtn) {
      openViewStudent(parseInt(viewBtn.getAttribute("data-id"), 10));
      return;
    }
    var editBtn = ev.target.closest(".btn-edit");
    if (editBtn) {
      openStudentModal(true, parseInt(editBtn.getAttribute("data-id"), 10));
      return;
    }
    var delBtn = ev.target.closest(".btn-del");
    if (delBtn) {
      confirmDeleteStudent(
        parseInt(delBtn.getAttribute("data-id"), 10),
        delBtn.getAttribute("data-name") || ""
      );
    }
  });

  $("btn-confirm-delete").addEventListener("click", doDeleteStudent);

  document.querySelectorAll("[data-close-modal]").forEach(function (el) {
    el.addEventListener("click", closeModals);
  });

  if (requireAuth()) {
    enterApp();
  } else {
    showSection("login");
  }
});
