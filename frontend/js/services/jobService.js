// frontend/js/services/jobService.js

import { api } from "../core/api.js";
import { store } from "../core/store.js";

export const jobService = {
  async list() {
    const jobs = await api.get("/jobs/");
    store.set("jobs", jobs);
    return jobs;
  },

  async get(id) {
    return api.get(`/jobs/${id}/`);
  },

  async uploadScreenshot(file) {
    const form = new FormData();
    form.append("screenshot", file);
    return api.upload("/jobs/upload/", form);
  },
};