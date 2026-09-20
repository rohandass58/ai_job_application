// frontend/js/services/applicationService.js

import { api } from "../core/api.js";
import { store } from "../core/store.js";

export const applicationService = {
  async list() {
    const apps = await api.get("/applications/");
    store.set("applications", apps);
    return apps;
  },

  async get(id) {
    return api.get(`/applications/${id}/`);
  },

  async create(jobPostId, resumeId = null) {
    return api.post("/applications/create/", {
      job_post_id: jobPostId,
      resume_id: resumeId,
    });
  },

  async update(id, { subject, body, to_email }) {
    return api.patch(`/applications/${id}/`, { subject, body, to_email });
  },

  async send(id) {
    return api.post(`/applications/${id}/send/`, {});
  },
};