/**
 * ============================================================
 * AAROGYA — SEARCH RESULTS SCRIPT
 * js/search-results.js
 *
 * Responsibilities:
 * - Read ?q= from URL
 * - Call GET /api/search?q=<query>
 * - Render loading skeleton, results, empty, or error state
 * - Wire the top search bar (submit / Enter re-searches)
 * - Handle medicine card clicks → medicine details (placeholder)
 * ============================================================
 */

(() => {

  // ============================================================
  // ELEMENTS
  // ============================================================

  const els = {
    form:        document.getElementById('results-search-form'),
    input:       document.getElementById('results-search-input'),
    header:      document.getElementById('results-header'),
    title:       document.getElementById('results-title'),
    count:       document.getElementById('results-count'),
    content:     document.getElementById('results-content'),
  };

  // ============================================================
  // HELPERS — DOM
  // ============================================================

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatPrice(value) {
    if (value === null || value === undefined) return '—';
    const num = Number(value);
    if (Number.isNaN(num)) return '—';
    return `₹${num.toFixed(2)}`;
  }

  function getQueryFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return (params.get('q') || '').trim();
  }

  function setDocTitle(query) {
    document.title = query
      ? `Search: ${query} — Aarogya`
      : 'Search — Aarogya';
  }

  // ============================================================
  // RENDER — HEADER
  // ============================================================

  function renderHeader(query, count) {
    if (!els.title || !els.count) return;

    if (query) {
      els.title.innerHTML = `Results for
        <span class="results-title-query">"${escapeHtml(query)}"</span>`;
    } else {
      els.title.textContent = 'Search Medicines';
    }

    if (count === null || count === undefined) {
      els.count.textContent = '';
    } else {
      els.count.textContent =
        count === 1 ? '1 result' : `${count} results`;
    }
  }

  // ============================================================
  // RENDER — LOADING SKELETON
  // ============================================================

  function renderLoading() {
    if (!els.content) return;

    const skeletonCard = `
      <div class="skeleton-card" aria-busy="true" aria-label="Loading medicine">
        <div class="skeleton-card-header">
          <div style="flex: 1;">
            <div class="skeleton skeleton-heading skeleton-line-3-4"></div>
            <div class="skeleton skeleton-text-sm skeleton-line-half"></div>
          </div>
          <div class="skeleton skeleton-badge"></div>
        </div>
        <div class="skeleton-card-lines">
          <div class="flex gap-2">
            <div class="skeleton skeleton-badge" style="width: 60px;"></div>
            <div class="skeleton skeleton-badge" style="width: 70px;"></div>
          </div>
          <div class="skeleton skeleton-text skeleton-line-full"
               style="height: 64px; border-radius: var(--radius-md);"></div>
          <div class="skeleton skeleton-text skeleton-line-full"
               style="height: 42px; border-radius: var(--radius-md);"></div>
          <div class="skeleton skeleton-button"></div>
        </div>
      </div>
    `;

    els.content.innerHTML = `
      <div class="results-grid" aria-busy="true">
        ${skeletonCard.repeat(6)}
      </div>
    `;
  }

  // ============================================================
  // RENDER — EMPTY STATE
  // ============================================================

  function renderEmpty(query) {
    if (!els.content) return;

    els.content.innerHTML = `
      <div class="results-state">
        <div class="empty-state">
          <div class="empty-state-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="1.5"
              stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
              <line x1="8" y1="11" x2="14" y2="11"/>
            </svg>
          </div>
          <h2 class="empty-state-title">No medicines matched your search</h2>
          <p class="empty-state-description">
            We couldn't find any medicines for
            <strong>"${escapeHtml(query)}"</strong>.
            Try a different name or check the spelling.
          </p>
          <div class="empty-state-actions">
            <a href="home.html" class="btn btn-primary">Back to Search</a>
            <button type="button"
              class="btn btn-ghost"
              data-focus-search>
              Try Another Search
            </button>
          </div>
        </div>
      </div>
    `;

    const focusBtn = els.content.querySelector('[data-focus-search]');
    if (focusBtn && els.input) {
      focusBtn.addEventListener('click', () => {
        els.input.focus();
        els.input.select();
      });
    }
  }

  // ============================================================
  // RENDER — ERROR STATE
  // ============================================================

  function renderError(errorCode) {
    if (!els.content) return;

    const codeHtml = errorCode
      ? `<div class="error-state-code" role="note">${escapeHtml(errorCode)}</div>`
      : '';

    els.content.innerHTML = `
      <div class="results-state">
        <div class="error-state">
          <div class="error-state-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="1.5"
              stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <h2 class="error-state-title">Unable to retrieve medicines</h2>
          <p class="error-state-description">
            We couldn't reach the medicine service.
            Please check your connection and try again.
          </p>
          ${codeHtml}
          <div class="error-state-actions">
            <button type="button" class="btn btn-primary" data-retry>Retry</button>
            <a href="home.html" class="btn btn-ghost">Go Home</a>
          </div>
        </div>
      </div>
    `;

    const retryBtn = els.content.querySelector('[data-retry]');
    if (retryBtn) {
      retryBtn.addEventListener('click', () => {
        runSearch(getQueryFromUrl());
      });
    }
  }

  // ============================================================
  // RENDER — MEDICINE CARD
  // ============================================================

  function buildMedicineCard(medicine) {
    const {
      medicine_id,
      brand_name,
      generic_name,
      dosage,
      form,
      brand_price,
      generic_price,
      savings_percent,
      match_type,
    } = medicine;

    const matchBadge = match_type === 'brand'
      ? '<span class="badge badge-accent">Brand Match</span>'
      : '<span class="badge badge-primary">Generic Match</span>';

    const hasSavings =
      savings_percent !== null &&
      savings_percent !== undefined &&
      Number(savings_percent) > 0;

    const savingsBlock = hasSavings
      ? `
        <div class="medicine-card-savings">
          <span class="savings-icon" aria-hidden="true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </span>
          <span class="savings-text">
            Save
            <span class="savings-percent">${Number(savings_percent).toFixed(1)}%</span>
            with the generic
          </span>
        </div>`
      : '';

    return `
      <button
        type="button"
        class="medicine-card"
        data-medicine-id="${escapeHtml(medicine_id)}"
        aria-label="View details for ${escapeHtml(brand_name)} — ${escapeHtml(generic_name)}"
      >
        <div class="medicine-card-header">
          <div class="medicine-card-brand">
            <span class="medicine-card-brand-name">${escapeHtml(brand_name)}</span>
            <span class="medicine-card-generic">${escapeHtml(generic_name)}</span>
          </div>
          ${matchBadge}
        </div>

        <div class="medicine-card-meta">
          ${dosage ? `<span class="medicine-meta-pill">${escapeHtml(dosage)}</span>` : ''}
          ${form   ? `<span class="medicine-meta-pill">${escapeHtml(form)}</span>`   : ''}
        </div>

        <div class="medicine-card-prices">
          <div class="price-cell">
            <span class="price-label">Generic</span>
            <span class="price-value price-generic">${formatPrice(generic_price)}</span>
          </div>
          <div class="price-cell">
            <span class="price-label">Avg Brand</span>
            <span class="price-value price-brand">${formatPrice(brand_price)}</span>
          </div>
        </div>

        ${savingsBlock}

        <div class="medicine-card-footer">
          <div class="medicine-card-badges">
            <span class="badge-verified">
              <svg class="badge-icon" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2.5"
                stroke-linecap="round" stroke-linejoin="round"
                aria-hidden="true">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Verified
            </span>
          </div>
          <span class="medicine-card-cta">
            View Details
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round"
              aria-hidden="true">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </span>
        </div>
      </button>
    `;
  }

  // ============================================================
  // RENDER — RESULTS
  // ============================================================

  function renderResults(results) {
    if (!els.content) return;

    const cards = results.map(buildMedicineCard).join('');

    els.content.innerHTML = `
      <div class="results-grid">
        ${cards}
      </div>
    `;

    // Wire card clicks — navigate to medicine details (placeholder)
    els.content.querySelectorAll('[data-medicine-id]').forEach((card) => {
      card.addEventListener('click', () => {
        const id = card.getAttribute('data-medicine-id');
        goToMedicineDetails(id);
      });
    });
  }

  // ============================================================
  // NAVIGATION — placeholder for Sprint 4
  // ============================================================

  function goToMedicineDetails(medicineId) {
    if (!medicineId) return;
    // Sprint 4 will create pages/medicine.html
    // For now, keep the intent visible and testable
    window.location.href =
      `medicine.html?id=${encodeURIComponent(medicineId)}`;
  }

  // ============================================================
  // API CALL
  // ============================================================

  async function fetchSearch(query) {
    const url = window.AarogyaConfig.url(
      window.AarogyaConfig.endpoints.search(query)
    );

    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) {
      const err = new Error(`HTTP ${response.status}`);
      err.code = `HTTP_${response.status}`;
      throw err;
    }

    const data = await response.json();

    if (!Array.isArray(data)) {
      const err = new Error('Unexpected response shape');
      err.code = 'BAD_RESPONSE';
      throw err;
    }

    return data;
  }

  // ============================================================
  // MAIN SEARCH FLOW
  // ============================================================

  async function runSearch(query) {
    setDocTitle(query);

    if (els.input) {
      els.input.value = query;
    }

    // No query — send user back home rather than showing empty
    if (!query) {
      renderHeader('', null);
      renderEmpty('');
      return;
    }

    renderHeader(query, null);
    renderLoading();

    try {
      const results = await fetchSearch(query);

      renderHeader(query, results.length);

      if (results.length === 0) {
        renderEmpty(query);
      } else {
        renderResults(results);
      }
    } catch (error) {
      console.error('[Aarogya] Search failed:', error);
      renderHeader(query, null);
      renderError(error.code || 'NETWORK_ERROR');
    }
  }

  // ============================================================
  // WIRE — top search bar
  // ============================================================

  function wireSearchBar() {
    if (els.form) {
      els.form.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = (els.input?.value || '').trim();
        if (!query) {
          els.input?.focus();
          return;
        }
        // Update the URL without full reload, then re-search
        const newUrl =
          `${window.location.pathname}?q=${encodeURIComponent(query)}`;
        window.history.pushState({ query }, '', newUrl);
        runSearch(query);
      });
    }

    if (els.input) {
      els.input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          els.form?.requestSubmit();
        }
      });
    }

    // Back / forward button support
    window.addEventListener('popstate', () => {
      runSearch(getQueryFromUrl());
    });
  }

  // ============================================================
  // INIT
  // ============================================================

  document.addEventListener('DOMContentLoaded', () => {
    wireSearchBar();
    runSearch(getQueryFromUrl());
  });

})();
