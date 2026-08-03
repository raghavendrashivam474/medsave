/**
 * ============================================================
 * AAROGYA — GLOBAL CONFIG
 * js/config.js
 *
 * Single source of truth for backend URLs.
 * Change the API base here and every page updates automatically.
 * ============================================================
 */

window.AarogyaConfig = {
  API_BASE: 'http://localhost:5000',

  endpoints: {
    search:   (query)     => `/api/search?q=${encodeURIComponent(query)}`,
    medicine: (id)        => `/api/medicine/${id}`,
    stores:   ()          => `/api/stores`,
    health:   ()          => `/api/health`,
  },

  /**
   * Build a full URL from an endpoint helper.
   * Usage: AarogyaConfig.url(AarogyaConfig.endpoints.search('crocin'))
   */
  url(path) {
    return `${this.API_BASE}${path}`;
  },
};
