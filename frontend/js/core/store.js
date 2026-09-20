// frontend/js/core/store.js

const state = {
  user: null,
  resumes: [],
  jobs: [],
  applications: [],
};

const listeners = new Set();

export const store = {
  get(key) {
    return state[key];
  },

  set(key, value) {
    state[key] = value;
    listeners.forEach((fn) => fn(key, value));
  },

  subscribe(fn) {
    listeners.add(fn);
    return () => listeners.delete(fn);
  },
};