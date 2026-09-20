// frontend/js/screens/uploadScreen.js

import { bottomNav } from "../components/bottomNav.js";
import { pageLoader } from "../components/loader.js";
import { pageHeader } from "../components/pageHeader.js";
import { navigate } from "../core/router.js";
import { showToast } from "../core/toast.js";
import { applicationService } from "../services/applicationService.js";
import { jobService } from "../services/jobService.js";
import { resumeService } from "../services/resumeService.js";
import { $, esc, formatBytes, mount, setLoading } from "../utils/dom.js";

const MAX_MB = 5;
const ALLOWED = ["image/jpeg", "image/png", "image/webp"];

const ANALYZE_STEPS = [
  "Uploading screenshot...",
  "Reading the job post...",
  "Extracting company & skills...",
  "Almost done...",
];

function shell(inner) {
  return `<div class="page">${inner}</div>${bottomNav("/home")}`;
}

function validateImage(file) {
  if (!file) return "Choose an image";
  if (!ALLOWED.includes(file.type)) return "Only JPG, PNG or WEBP images are allowed";
  if (file.size > MAX_MB * 1024 * 1024) return `Image must be under ${MAX_MB} MB`;
  return null;
}

// ---------- Step 1: pick + preview ----------
function renderPicker() {
  mount(
    shell(`
      ${pageHeader({ title: "New Application", subtitle: "Upload a screenshot of the job post", backTo: "/home" })}

      <form class="card" id="uploadForm" novalidate>
        <label for="shot" class="dropzone" id="dropzone">
          <div class="dropzone-icon">📸</div>
          <div>Tap to choose a screenshot</div>
          <div class="muted">JPG, PNG or WEBP, up to ${MAX_MB} MB</div>
        </label>
        <input type="file" id="shot" accept="image/jpeg,image/png,image/webp" hidden />

        <div id="previewBox" hidden>
          <img id="preview" class="preview" alt="Job screenshot preview" />
          <div id="fileInfo" class="muted" style="margin:8px 0 14px"></div>
        </div>

        <button type="submit" class="btn btn-primary" id="analyzeBtn" disabled>Analyze with AI</button>
      </form>
    `)
  );

  let previewUrl = null;

  $("#shot").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const problem = validateImage(file);
    if (problem) {
      showToast(problem, "error");
      e.target.value = "";
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl); // avoid memory leak
    previewUrl = URL.createObjectURL(file);

    $("#preview").src = previewUrl;
    $("#fileInfo").textContent = `${file.name} (${formatBytes(file.size)})`;
    $("#previewBox").hidden = false;
    $("#dropzone").hidden = true;
    $("#analyzeBtn").disabled = false;
  });

  $("#uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = $("#shot").files[0];
    const problem = validateImage(file);
    if (problem) {
      showToast(problem, "error");
      return;
    }
    await analyze(file);
  });
}

// ---------- Step 2: analyze (slow AI call) ----------
async function analyze(file) {
  mount(shell(pageLoader(ANALYZE_STEPS[0])));

  // Rotate the loading text so the user knows it is alive
  let i = 0;
  const ticker = setInterval(() => {
    i = Math.min(i + 1, ANALYZE_STEPS.length - 1);
    const el = document.querySelector(".page-loader p");
    if (el) el.textContent = ANALYZE_STEPS[i];
  }, 3500);

  try {
    const job = await jobService.uploadScreenshot(file);
    clearInterval(ticker);
    renderResult(job);
  } catch (err) {
    clearInterval(ticker);

    const msg =
      err.status === 429
        ? "You have reached the hourly AI limit. Try again later."
        : err.message || "Could not read the screenshot";

    showToast(msg, "error");
    renderPicker();
  }
}

// ---------- Step 3: show parsed result ----------
function renderResult(job) {
  const skills = Array.isArray(job.skills) ? job.skills : [];
  const noEmail = !job.hr_email;

  mount(
    shell(`
      ${pageHeader({ title: "Check details", subtitle: "AI can make mistakes. Verify before continuing." })}

      <div class="card">
        <div class="detail-row"><span class="muted">Company</span><strong>${esc(job.company) || "Not found"}</strong></div>
        <div class="detail-row"><span class="muted">Role</span><strong>${esc(job.role) || "Not found"}</strong></div>
        <div class="detail-row"><span class="muted">Location</span><strong>${esc(job.location) || "Not found"}</strong></div>
        <div class="detail-row"><span class="muted">HR email</span><strong>${esc(job.hr_email) || "Not found"}</strong></div>

        ${
          skills.length
            ? `<div class="chips">${skills.map((s) => `<span class="chip">${esc(s)}</span>`).join("")}</div>`
            : ""
        }
      </div>

      ${
        noEmail
          ? `<div class="card notice"><strong>No HR email found</strong>
             <p class="muted" style="margin-top:6px">You can add the recipient on the next screen.</p></div>`
          : ""
      }

      <button class="btn btn-primary" id="generateBtn">Generate Email</button>
      <button class="btn btn-outline btn-block" id="retryBtn" style="margin-top:10px">Use a different screenshot</button>
    `)
  );

  $("#retryBtn").onclick = renderPicker;

  $("#generateBtn").onclick = async () => {
    const restore = setLoading($("#generateBtn"), "Writing your email...");
    try {
      const resumes = await resumeService.list();
      const primary = resumes.find((r) => r.is_primary) || resumes[0];

      if (!primary) {
        showToast("Upload a resume first", "error");
        navigate("/resumes");
        return;
      }

      const app = await applicationService.create(job.id, primary.id);
      showToast("Email drafted!", "success");
      navigate(`/applications/${app.id}`);
    } catch (err) {
      const msg = err.status === 429 ? "AI limit reached. Try again later." : err.message;
      showToast(msg || "Could not generate email", "error");
      restore();
    }
  };
}

export function uploadScreen() {
  renderPicker();
}