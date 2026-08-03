/**
 * ============================================================
 * AAROGYA — TRUST PASSPORT
 * js/trust-passport.js
 *
 * A self-contained module that:
 *  - Injects the Trust Passport dialog into the page on first use
 *  - Opens on click of any [data-open-trust-passport]
 *  - Closes on X, "Got It", Escape, or overlay click
 *  - Traps focus while open
 *  - Restores focus to the trigger on close
 *  - Populates content from a data source (mock for now,
 *    ready for a future GET /api/trust/<id> endpoint)
 * ============================================================
 */

(() => {

  // ============================================================
  // MOCK DATA
  // Replace with a backend call in a future milestone.
  // Signature is intentionally close to a future API response.
  // ============================================================

  const DEFAULT_PASSPORT = {
    verified: true,
    sources: [
      {
        name: 'PMBI',
        purpose: 'Jan Aushadhi generic medicine catalogue',
        status: 'Active',
      },
      {
        name: 'CDSCO',
        purpose: 'Central drug approvals and standards',
        status: 'Active',
      },
      {
        name: 'NPPA',
        purpose: 'National pharmaceutical pricing authority',
        status: 'Active',
      },
    ],
    lastChecked: new Date(),
    lastUpdated: new Date(),
    version: 'v1.0',
    checks: [
      'Medicine name verified',
      'Pricing checked',
      'Generic equivalent confirmed',
      'Manufacturer validated',
      'Duplicate records removed',
    ],
    freshness:
      'Information is regularly reviewed and updated using trusted healthcare datasets.',
  };

  // ============================================================
  // STATE
  // ============================================================

  const state = {
    overlay:        null,
    dialog:         null,
    lastTrigger:    null,
    keydownHandler: null,
    focusables:     [],
    injected:       false,
  };

  // ============================================================
  // HELPERS
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

  function formatDate(d) {
    if (!d) return '—';
    const date = d instanceof Date ? d : new Date(d);
    if (Number.isNaN(date.getTime())) return '—';
    return date.toLocaleDateString('en-IN', {
      day: 'numeric', month: 'short', year: 'numeric',
    });
  }

  // ============================================================
  // MARKUP
  // ============================================================

  function buildSourceCard(source) {
    return `
      <div class="tp-source-card">
        <div class="tp-source-card-top">
          <span class="tp-source-name">${escapeHtml(source.name)}</span>
          <span class="tp-source-status">${escapeHtml(source.status)}</span>
        </div>
        <p class="tp-source-purpose">${escapeHtml(source.purpose)}</p>
      </div>
    `;
  }

  function buildCheck(text) {
    return `
      <div class="tp-check">
        <span class="tp-check-icon" aria-hidden="true">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="3"
            stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </span>
        <span class="tp-check-text">${escapeHtml(text)}</span>
      </div>
    `;
  }

  function buildDialog(data) {
    const sources = (data.sources || []).map(buildSourceCard).join('');
    const checks  = (data.checks  || []).map(buildCheck).join('');

    return `
      <div class="tp-overlay" id="trust-passport" role="presentation" aria-hidden="true">
        <div
          class="tp-dialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby="tp-title"
          aria-describedby="tp-status-desc"
          tabindex="-1"
        >

          <header class="tp-header">
            <div class="tp-header-title-block">
              <div class="tp-header-icon" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </div>
              <div class="tp-header-text">
                <h2 class="tp-title" id="tp-title">Trust Passport</h2>
                <p class="tp-subtitle">
                  Understand why this medicine information can be trusted.
                </p>
              </div>
            </div>
            <button
              type="button"
              class="tp-close"
              data-tp-close
              aria-label="Close Trust Passport"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </header>

          <div class="tp-body">

            <!-- Section 2 — Verification Status -->
            <section class="tp-section">
              <div class="tp-status">
                <div class="tp-status-icon" aria-hidden="true">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2.5"
                    stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
                <div class="tp-status-text">
                  <span class="tp-status-title">Verified</span>
                  <span class="tp-status-desc" id="tp-status-desc">
                    This medicine has been validated using trusted healthcare sources.
                  </span>
                </div>
              </div>
            </section>

            <!-- Section 3 — Trusted Sources -->
            <section class="tp-section" aria-labelledby="tp-sources-heading">
              <h3 class="tp-section-heading" id="tp-sources-heading">
                Trusted Sources
              </h3>
              <div class="tp-sources">
                ${sources}
              </div>
            </section>

            <!-- Section 4 — Last Verification -->
            <section class="tp-section" aria-labelledby="tp-timeline-heading">
              <h3 class="tp-section-heading" id="tp-timeline-heading">
                Last Verification
              </h3>
              <div class="tp-timeline">
                <div class="tp-timeline-item">
                  <span class="tp-timeline-label">Last Checked</span>
                  <span class="tp-timeline-value">${escapeHtml(formatDate(data.lastChecked))}</span>
                </div>
                <div class="tp-timeline-item">
                  <span class="tp-timeline-label">Last Updated</span>
                  <span class="tp-timeline-value">${escapeHtml(formatDate(data.lastUpdated))}</span>
                </div>
                <div class="tp-timeline-item">
                  <span class="tp-timeline-label">Version</span>
                  <span class="tp-timeline-value">${escapeHtml(data.version || '—')}</span>
                </div>
              </div>
            </section>

            <!-- Section 5 — Validation Summary -->
            <section class="tp-section" aria-labelledby="tp-checks-heading">
              <h3 class="tp-section-heading" id="tp-checks-heading">
                Validation Summary
              </h3>
              <div class="tp-checks">
                ${checks}
              </div>
            </section>

            <!-- Section 6 — Data Freshness -->
            <section class="tp-section" aria-labelledby="tp-fresh-heading">
              <h3 class="tp-section-heading" id="tp-fresh-heading">
                Data Freshness
              </h3>
              <div class="tp-fresh">
                <span class="tp-fresh-icon" aria-hidden="true">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2"
                    stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="23 4 23 10 17 10"/>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
                  </svg>
                </span>
                <p class="tp-fresh-text">
                  ${escapeHtml(data.freshness || '')}
                </p>
              </div>
            </section>

            <!-- Section 7 — Learn More (collapsible) -->
            <section class="tp-section" aria-labelledby="tp-learn-heading">
              <h3 class="tp-section-heading" id="tp-learn-heading">
                Learn More
              </h3>
              <details class="tp-learn">
                <summary class="tp-learn-summary">
                  <span>How Aarogya validates information</span>
                  <span class="tp-learn-chevron" aria-hidden="true">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="2"
                      stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="6 9 12 15 18 9"/>
                    </svg>
                  </span>
                </summary>
                <div class="tp-learn-content">
                  <p>
                    Every medicine entry is compiled from publicly available
                    healthcare records and cross-checked against the Government
                    of India&rsquo;s Jan Aushadhi catalogue.
                  </p>
                  <p>
                    Duplicate entries are removed, missing fields are flagged,
                    and pricing is normalised against official generic listings.
                  </p>
                  <p>
                    A public source-attribution log is planned so anyone can
                    inspect exactly how a medicine record was assembled.
                  </p>
                </div>
              </details>
            </section>

          </div>

          <!-- Section 8 — Footer -->
          <footer class="tp-footer">
            <button
              type="button"
              class="btn btn-primary btn-sm"
              data-tp-close
              data-tp-primary
            >
              Got It
            </button>
          </footer>

        </div>
      </div>
    `;
  }

  // ============================================================
  // INJECTION — build the passport DOM once, reuse thereafter
  // ============================================================

  function inject(data) {
    if (state.injected) return;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = buildDialog(data).trim();
    document.body.appendChild(wrapper.firstChild);

    state.overlay = document.getElementById('trust-passport');
    state.dialog  = state.overlay.querySelector('.tp-dialog');

    // Overlay click closes
    state.overlay.addEventListener('click', (e) => {
      if (e.target === state.overlay) close();
    });

    // Close buttons
    state.overlay.querySelectorAll('[data-tp-close]').forEach((btn) => {
      btn.addEventListener('click', close);
    });

    state.injected = true;
  }

  // ============================================================
  // FOCUS TRAP
  // ============================================================

  const FOCUSABLE_SELECTOR = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'textarea:not([disabled])',
    'select:not([disabled])',
    'details > summary',
    '[tabindex]:not([tabindex="-1"])',
  ].join(',');

  function refreshFocusables() {
    state.focusables = Array.from(
      state.dialog.querySelectorAll(FOCUSABLE_SELECTOR)
    ).filter((el) => el.offsetParent !== null || el === document.activeElement);
  }

  function onKeydown(e) {
    if (!state.overlay || !state.overlay.classList.contains('open')) return;

    if (e.key === 'Escape') {
      e.preventDefault();
      close();
      return;
    }

    if (e.key !== 'Tab') return;

    refreshFocusables();
    if (state.focusables.length === 0) {
      e.preventDefault();
      state.dialog.focus();
      return;
    }

    const first = state.focusables[0];
    const last  = state.focusables[state.focusables.length - 1];
    const active = document.activeElement;

    if (e.shiftKey && active === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && active === last) {
      e.preventDefault();
      first.focus();
    }
  }

  // ============================================================
  // OPEN / CLOSE
  // ============================================================

  function open(trigger, data) {
    inject(data || DEFAULT_PASSPORT);

    state.lastTrigger = trigger || document.activeElement;

    state.overlay.classList.add('open');
    state.overlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // Attach global keydown once per open
    state.keydownHandler = onKeydown;
    document.addEventListener('keydown', state.keydownHandler);

    // Move focus into the dialog on the next tick
    // (so the browser paints the overlay first)
    requestAnimationFrame(() => {
      refreshFocusables();
      const primary =
        state.dialog.querySelector('[data-tp-primary]') ||
        state.focusables[0] ||
        state.dialog;
      primary.focus();
    });
  }

  function close() {
    if (!state.overlay) return;

    state.overlay.classList.remove('open');
    state.overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';

    if (state.keydownHandler) {
      document.removeEventListener('keydown', state.keydownHandler);
      state.keydownHandler = null;
    }

    if (state.lastTrigger && typeof state.lastTrigger.focus === 'function') {
      state.lastTrigger.focus();
    }
    state.lastTrigger = null;
  }

  // ============================================================
  // AUTO-WIRE any [data-open-trust-passport] on the page
  // ============================================================

  function wireTriggers() {
    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('[data-open-trust-passport]');
      if (!trigger) return;
      e.preventDefault();
      open(trigger);
    });
  }

  // ============================================================
  // PUBLIC API
  // ============================================================

  window.TrustPassport = {
    open,
    close,
    /**
     * Provide a custom passport payload for the next open() call.
     * Ready for future backend integration:
     *
     *   TrustPassport.setData(await fetch('/api/trust/1').then(r => r.json()));
     *   TrustPassport.open();
     */
    setData(data) {
      // Force a fresh injection with new data
      if (state.injected && state.overlay) {
        state.overlay.remove();
        state.injected = false;
        state.overlay = null;
        state.dialog  = null;
      }
      inject(data || DEFAULT_PASSPORT);
    },
  };

  // ============================================================
  // INIT
  // ============================================================

  document.addEventListener('DOMContentLoaded', wireTriggers);

})();
