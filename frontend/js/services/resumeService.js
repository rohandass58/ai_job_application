// frontend/js/services/resumeService.js

import { api } from "../core/api.js";
import { store } from "../core/store.js";

export const resumeService = {
  async list() {
    const resumes = await api.get("/resumes/");
    store.set("resumes", resumes);
    return resumes;
  },

  async upload({ file, title, isPrimary = true }) {
    const form = new FormData();
    form.append("file", file);
    form.append("title", title || "My Resume");
    form.append("is_primary", isPrimary ? "true" : "false");
    return api.upload("/resumes/upload/", form);
  },
};