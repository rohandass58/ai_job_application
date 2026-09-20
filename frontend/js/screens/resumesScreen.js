// frontend/js/screens/resumesScreen.js

import { bottomNav } from "../components/bottomNav.js";
import { emptyState, pageLoader } from "../components/loader.js";
import { pageHeader } from "../components/pageHeader.js";
import { showToast } from "../core/toast.js";
import { resumeService } from "../services/resumeService.js";
import { $, esc, formatBytes, mount, setLoading, timeAgo } from "../utils/dom.js";

const MAX_MB = 5;

function shell(inner) {
  return `<div class="page">${inner}</div>${bottomNav("/profile")}`;
}

function resumeItem(r) {
  return `
    <div class="list-item">
      <div class="list-main">
        <div class="list-title">${esc(r.title)} ${r.is_primary ? `<span class="badge badge-info">Primary</span>` : ""}</div>
        <div class="muted">
          Uploaded ${timeAgo(r.created_at)}
          ${r.has_text ? "" : " · ⚠️ text could not be read"}
        </div>
      </div>
    </div>`;
}

function validateFile(file) {
  if (!file) return "Choose a PDF file";
  if (!file.name.toLowerCase().endsWith(".pdf")) return "Only PDF files are allowed";
  if (file.size > MAX_MB * 1024 * 1024) return `File must be under ${MAX_MB} MB`;
  return null;
}

function renderList(resumes) {
  const box = $("#resumeList");
  box.innerHTML = resumes.length
    ? `<div class="card list-card">${resumes.map(resumeItem).join("")}</div>`
    : emptyState({ icon: "📄", title: "No resume yet", text: "Upload a PDF to get started." });
}

export async function resumesScreen() {
  mount(shell(pageLoader("Loading resumes...")));

  try {
    const resumes = await resumeService.list();

    mount(
      shell(`
        ${pageHeader({ title: "My Resumes", subtitle: "PDF only, up to 5 MB", backTo: "/profile" })}

        <form class="card" id="resumeForm" novalidate>
          <div class="form-group">
            <label for="resumeTitle">Title</label>
            <input type="text" id="resumeTitle" value="My Resume" maxlength="150" />
          </div>

          <div class="form-group">
            <label for="resumeFile">PDF file</label>
            <input type="file" id="resumeFile" accept="application/pdf,.pdf" />
            <div id="fileInfo" class="muted" style="margin-top:6px"></div>
          </div>

          <button type="submit" class="btn btn-primary" id="resumeBtn">Upload Resume</button>
        </form>

        <div class="section-head"><h3>Uploaded</h3></div>
        <div id="resumeList"></div>
      `)
    );

    renderList(resumes);

    $("#resumeFile").addEventListener("change", (e) => {
      const file = e.target.files[0];
      const info = $("#fileInfo");
      if (!file) {
        info.textContent = "";
        return;
      }
      const problem = validateFile(file);
      info.textContent = problem ? `❌ ${problem}` : `✅ ${file.name} (${formatBytes(file.size)})`;
    });

    $("#resumeForm").addEventListener("submit", async (e) => {
      e.preventDefault();

      const file = $("#resumeFile").files[0];
      const problem = validateFile(file);
      if (problem) {
        showToast(problem, "error");
        return;
      }

      const restore = setLoading($("#resumeBtn"), "Uploading...");
      try {
        await resumeService.upload({
          file,
          title: $("#resumeTitle").value.trim() || "My Resume",
        });
        showToast("Resume uploaded!", "success");

        const fresh = await resumeService.list();
        renderList(fresh);
        $("#resumeForm").reset();
        $("#resumeTitle").value = "My Resume";
        $("#fileInfo").textContent = "";
      } catch (err) {
        const detail = err.errors?.file ? ` ${[].concat(err.errors.file).join(" ")}` : "";
        showToast((err.message || "Upload failed") + detail, "error");
      } finally {
        restore();
      }
    });
  } catch (err) {
    showToast(err.message || "Failed to load resumes", "error");
    mount(
      shell(
        emptyState({
          icon: "⚠️",
          title: "Could not load resumes",
          text: err.message,
          actionHtml: `<button class="btn btn-primary btn-sm" onclick="location.reload()">Retry</button>`,
        })
      )
    );
  }
}