/**
 * ============================================================
 * AAROGYA — MEDICINE PROFILE SCRIPT
 * js/medicine.js
 *
 * Responsibilities:
 * - Read ?id= from URL
 * - Call GET /api/medicine/<id>
 * - Render loading skeleton, then medicine profile
 * - Handle empty / error states
 *
 * Trust Passport (Sprint 5) is a separate module.
 * We simply mark the trust button with
 *   data-open-trust-passport
 * and window.TrustPassport auto-wires it.
 * ============================================================
 */

(() => {

  // ============================================================
  // ELEMENTS
  // ============================================================

  const els = {
    container: document.getElementById('medicine-page'),
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

  function formatPrice(value) {
    if (value === null || value === undefined) return '—';
    const num = Number(value);
    if (Number.isNaN(num)) return '—';
    return `?${num.toFixed(2)}`;
  }

  function isPresent(value) {
    return value !== null && value !== undefined && String(value).trim() !== '';
  }

  function getIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const raw = params.get('id');
    if (!raw) return null;
    const id = Number(raw);
    return Number.isInteger(id) && id > 0 ? id : null;
  }

  function setDocTitle(medicineName) {
    document.title = medicineName
      ? `${medicineName} — Aarogya`
      : 'Medicine — Aarogya';
  }

  function averageBrandPrice(brands) {
    if (!Array.isArray(brands) || brands.length === 0) return null;
    const valid = brands
      .map((b) => Number(b.mrp))
      .filter((n) => !Number.isNaN(n) && n > 0);
    if (valid.length === 0) return null;
    const sum = valid.reduce((acc, n) => acc + n, 0);
    return sum / valid.length;
  }

  function computeSavingsPercent(generic, brand) {
    if (!isPresent(generic) || !isPresent(brand)) return null;
    const g = Number(generic);
    const b = Number(brand);
    if (Number.isNaN(g) || Number.isNaN(b) || b <= 0) return null;
    if (b <= g) return 0;
    return Math.round(((b - g) / b) * 1000) / 10;
  }

  // ============================================================
  // RENDER — LOADING SKELETON
  // ============================================================

  function renderLoading() {
    els.container.innerHTML = `
      <div class="container">

        <nav class="med-breadcrumb" aria-label="Breadcrumb">
          <a class="med-breadcrumb-link" href="home.html">Home</a>
          <span class="med-breadcrumb-sep">/</span>
          <span class="med-breadcrumb-current">Loading...</span>
        </nav>

        <div class="med-hero" aria-busy="true">
          <div class="med-hero-top">
            <div style="flex: 1;">
              <div class="skeleton skeleton-heading" style="width: 60%; height: 44px;"></div>
              <div class="skeleton skeleton-text" style="width: 40%; margin-top: var(--space-3);"></div>
            </div>
            <div class="skeleton skeleton-badge" style="width: 100px;"></div>
          </div>
          <div class="flex gap-2 mt-4">
            <div class="skeleton skeleton-badge" style="width: 80px;"></div>
            <div class="skeleton skeleton-badge" style="width: 80px;"></div>
          </div>
          <div class="skeleton skeleton-text mt-6" style="height: 72px; border-radius: var(--radius-md);"></div>
        </div>

        <div class="med-layout">
          <div class="med-main">
            <div class="med-section" aria-busy="true">
              <div class="skeleton skeleton-heading" style="width: 30%;"></div>
              <div class="skeleton skeleton-text mt-4" style="height: 120px; border-radius: var(--radius-md);"></div>
            </div>
            <div class="med-section" aria-busy="true">
              <div class="skeleton skeleton-heading" style="width: 40%;"></div>
              <div class="flex flex-col gap-3 mt-4">
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text skeleton-line-3-4"></div>
                <div class="skeleton skeleton-text skeleton-line-half"></div>
              </div>
            </div>
            <div class="med-section" aria-busy="true">
              <div class="skeleton skeleton-heading" style="width: 35%;"></div>
              <div class="grid grid-auto-sm gap-3 mt-4">
                <div class="skeleton skeleton-text" style="height: 120px; border-radius: var(--radius-md);"></div>
                <div class="skeleton skeleton-text" style="height: 120px; border-radius: var(--radius-md);"></div>
                <div class="skeleton skeleton-text" style="height: 120px; border-radius: var(--radius-md);"></div>
              </div>
            </div>
          </div>
          <div class="med-sidebar">
            <div class="med-section" aria-busy="true">
              <div class="skeleton skeleton-text" style="height: 140px; border-radius: var(--radius-md);"></div>
            </div>
            <div class="med-section" aria-busy="true">
              <div class="skeleton skeleton-text" style="height: 160px; border-radius: var(--radius-md);"></div>
            </div>
          </div>
        </div>

      </div>
    `;
  }

  // ============================================================
  // RENDER — EMPTY STATE
  // ============================================================

  function renderNotFound(message) {
    els.container.innerHTML = `
      <div class="container">
        <div class="med-page-state">
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
            <h1 class="empty-state-title">Medicine not found</h1>
            <p class="empty-state-description">
              ${escapeHtml(message || "We couldn't find the medicine you're looking for. It may have been removed or the link is incorrect.")}
            </p>
            <div class="empty-state-actions">
              <a href="home.html" class="btn btn-primary">Back to Search</a>
              <button type="button" class="btn btn-ghost" onclick="window.history.back()">Go Back</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // ============================================================
  // RENDER — ERROR STATE
  // ============================================================

  function renderError(errorCode) {
    const codeHtml = errorCode
      ? `<div class="error-state-code" role="note">${escapeHtml(errorCode)}</div>`
      : '';

    els.container.innerHTML = `
      <div class="container">
        <div class="med-page-state">
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
            <h1 class="error-state-title">Unable to load medicine information</h1>
            <p class="error-state-description">
              We couldn't reach the medicine service.
              Please check your connection and try again.
            </p>
            ${codeHtml}
            <div class="error-state-actions">
              <button type="button" class="btn btn-primary" data-retry>Retry</button>
              <a href="home.html" class="btn btn-ghost">Back to Search</a>
            </div>
          </div>
        </div>
      </div>
    `;

    els.container.querySelector('[data-retry]')?.addEventListener('click', () => {
      loadMedicine(getIdFromUrl());
    });
  }

  // ============================================================
  // RENDER — HERO
  // ============================================================

  function renderHero(medicine, brands, avgBrand, savingsPercent) {
    const cheapestBrand = Array.isArray(brands) && brands.length > 0
      ? brands.reduce((min, b) => (b.mrp < min.mrp ? b : min), brands[0])
      : null;

    const brandCount = Array.isArray(brands) ? brands.length : 0;

    const hasSavings =
      savingsPercent !== null && savingsPercent !== undefined && savingsPercent > 0;

    const savingsRupees = hasSavings && isPresent(avgBrand)
      ? Number(avgBrand) - Number(medicine.jan_price)
      : null;

    const highlightHtml = hasSavings
      ? `
        <div class="med-hero-highlight">
          <div class="med-hero-highlight-icon" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
          <div class="med-hero-highlight-text">
            Generic version available.
            Save up to <strong>${formatPrice(savingsRupees)}</strong>
            (<strong>${savingsPercent.toFixed(1)}%</strong>)
            compared with branded alternatives.
          </div>
        </div>`
      : `
        <div class="med-hero-highlight">
          <div class="med-hero-highlight-icon" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div class="med-hero-highlight-text">
            Verified generic medicine information.
          </div>
        </div>`;

    const displayName = cheapestBrand
      ? cheapestBrand.brand_name
      : medicine.generic_name;

    setDocTitle(displayName);

    return `
      <div class="med-hero">
        <div class="med-hero-top">
          <div class="med-hero-badges">
            <span class="badge-verified">
              <svg class="badge-icon" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2.5"
                stroke-linecap="round" stroke-linejoin="round"
                aria-hidden="true">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Verified
            </span>
            ${isPresent(medicine.jan_price)
              ? '<span class="badge badge-primary">Jan Aushadhi Available</span>'
              : ''}
          </div>
        </div>

        <h1 class="med-hero-title">${escapeHtml(displayName)}</h1>
        <p class="med-hero-generic">
          Generic: <strong>${escapeHtml(medicine.generic_name)}</strong>
        </p>

        <div class="med-hero-meta">
          ${isPresent(medicine.dosage)
            ? `<span class="med-meta-pill">${escapeHtml(medicine.dosage)}</span>` : ''}
          ${isPresent(medicine.form)
            ? `<span class="med-meta-pill">${escapeHtml(medicine.form)}</span>` : ''}
          ${brandCount > 0
            ? `<span class="med-meta-pill">${brandCount} brand${brandCount === 1 ? '' : 's'} available</span>`
            : ''}
        </div>

        ${highlightHtml}
      </div>
    `;
  }

  // ============================================================
  // RENDER — PRICE COMPARISON
  // ============================================================

  function renderPriceCompare(medicine, avgBrand, savingsPercent) {
    const hasBrand = isPresent(avgBrand);
    const savingsRupees = hasBrand
      ? Number(avgBrand) - Number(medicine.jan_price)
      : null;

    return `
      <section class="med-section" aria-labelledby="price-heading">
        <div class="med-section-header">
          <div>
            <h2 class="med-section-title" id="price-heading">Price Comparison</h2>
            <p class="med-section-subtitle">
              Jan Aushadhi generic price vs. average branded MRP.
            </p>
          </div>
        </div>

        <div class="price-compare">

          <div class="price-tile">
            <span class="price-tile-label">Generic</span>
            <span class="price-tile-value value-generic">
              ${formatPrice(medicine.jan_price)}
            </span>
            <span class="price-tile-sub">Jan Aushadhi</span>
          </div>

          <div class="price-arrow" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </div>

          <div class="price-tile">
            <span class="price-tile-label">Avg Brand</span>
            <span class="price-tile-value value-brand">
              ${hasBrand ? formatPrice(avgBrand) : '—'}
            </span>
            <span class="price-tile-sub">Average MRP</span>
          </div>

          <div class="price-arrow" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </div>

          <div class="price-tile">
            <span class="price-tile-label">You Save</span>
            <span class="price-tile-value value-savings">
              ${hasBrand ? formatPrice(savingsRupees) : '—'}
            </span>
            ${hasBrand && savingsPercent !== null
              ? `<span class="price-savings-percent">${savingsPercent.toFixed(1)}% off</span>`
              : '<span class="price-tile-sub">—</span>'}
          </div>

        </div>
      </section>
    `;
  }

  // ============================================================
  // RENDER — MEDICINE INFORMATION
  // ============================================================

  function renderInfo(medicine) {
    const row = (label, value) => `
      <div class="info-row">
        <div class="info-label">${escapeHtml(label)}</div>
        <div class="info-value ${isPresent(value) ? '' : 'info-value-muted'}">
          ${isPresent(value) ? escapeHtml(value) : 'Not available'}
        </div>
      </div>
    `;

    return `
      <section class="med-section" aria-labelledby="info-heading">
        <div class="med-section-header">
          <div>
            <h2 class="med-section-title" id="info-heading">Medicine Information</h2>
            <p class="med-section-subtitle">
              Composition and classification details.
            </p>
          </div>
        </div>

        <div class="info-list">
          ${row('Generic Name',         medicine.generic_name)}
          ${row('Salt',                 medicine.salt)}
          ${row('Dosage',               medicine.dosage)}
          ${row('Form',                 medicine.form)}
          ${row('Manufacturer',         medicine.manufacturer)}
          ${row('Therapeutic Category', medicine.therapeutic_category)}
          ${row('Schedule',             medicine.schedule)}
        </div>
      </section>
    `;
  }

  // ============================================================
  // RENDER — AVAILABLE BRANDS
  // ============================================================

  function renderBrands(brands) {
    if (!Array.isArray(brands) || brands.length === 0) {
      return `
        <section class="med-section" aria-labelledby="brands-heading">
          <div class="med-section-header">
            <div>
              <h2 class="med-section-title" id="brands-heading">Available Brands</h2>
              <p class="med-section-subtitle">No branded alternatives listed.</p>
            </div>
          </div>
          <p class="text-body text-muted">
            Only the generic version is currently listed for this medicine.
          </p>
        </section>
      `;
    }

    const cheapestId = brands[0].id;

    const cards = brands.map((b) => {
      const isCheapest  = b.id === cheapestId;
      const savingsPct  = isPresent(b.savings_percent) ? Number(b.savings_percent) : null;
      const savingsHtml = savingsPct !== null && savingsPct > 0
        ? `<div class="brand-card-savings">Save ${savingsPct.toFixed(1)}%</div>`
        : '<div class="brand-card-savings" style="visibility:hidden;">—</div>';

      return `
        <article class="brand-card ${isCheapest ? 'brand-card-cheapest' : ''}">
          <div class="brand-card-header">
            <div>
              <div class="brand-card-name">${escapeHtml(b.brand_name)}</div>
              <div class="brand-card-manufacturer">
                ${isPresent(b.manufacturer) ? escapeHtml(b.manufacturer) : 'Manufacturer not listed'}
              </div>
            </div>
            ${isCheapest ? '<span class="badge badge-success">Cheapest</span>' : ''}
          </div>

          <div class="brand-card-price-row">
            <div class="brand-card-mrp">
              <span class="brand-card-mrp-label">MRP</span>
              <span class="brand-card-mrp-value">${formatPrice(b.mrp)}</span>
            </div>
            ${savingsHtml}
          </div>
        </article>
      `;
    }).join('');

    return `
      <section class="med-section" aria-labelledby="brands-heading">
        <div class="med-section-header">
          <div>
            <h2 class="med-section-title" id="brands-heading">
              Available Brands
            </h2>
            <p class="med-section-subtitle">
              ${brands.length} branded ${brands.length === 1 ? 'alternative' : 'alternatives'}
              sorted by price.
            </p>
          </div>
        </div>

        <div class="brand-grid">
          ${cards}
        </div>
      </section>
    `;
  }

  // ============================================================
  // RENDER — NEARBY STORES (Placeholder)
  // ============================================================

  // ── fetchStores ─────────────────────────────────────────────────────────────
  // Fetches live store data from the backend.
  // Returns a store array on success, empty array on any failure.
  // Does not touch the DOM — rendering is handled by renderStores().

  async function fetchStores() {
    try {
      const url = window.AarogyaConfig.url(
        window.AarogyaConfig.endpoints.stores()
      );

      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });

      if (!response.ok) {
        console.warn(`[MedSave] Stores API responded with status ${response.status}`);
        return [];
      }

      const json = await response.json();

      if (!json.success || !Array.isArray(json.data)) {
        console.warn('[MedSave] Stores API returned unexpected shape:', json);
        return [];
      }

      return json.data;

    } catch (error) {
      console.warn('[MedSave] Stores fetch failed:', error.message);
      return [];
    }
  }

  // ── renderStores ─────────────────────────────────────────────────────────────
  // Receives live store array from fetchStores().
  // Preserves existing card layout and CSS classes.

  function renderStores(stores) {

    // ── Empty state ───────────────────────────────────────────────────────────
    if (!stores || stores.length === 0) {
      return `
        <section class="med-section" aria-labelledby="stores-heading">
          <div class="med-section-header">
            <div>
              <h2 class="med-section-title" id="stores-heading">Nearby Jan Aushadhi</h2>
              <p class="med-section-subtitle">Jan Aushadhi store locations.</p>
            </div>
          </div>
          <div class="store-list">
            <div class="store-card">
              <div class="store-info">
                <div class="store-name">No stores found</div>
                <div class="store-address">
                  Visit
                  <a href="https://janaushadhi.gov.in" target="_blank" rel="noopener">
                    janaushadhi.gov.in
                  </a>
                  to locate your nearest store.
                </div>
              </div>
            </div>
          </div>
        </section>
      `;
    }

    // ── Store cards ───────────────────────────────────────────────────────────
    const cards = stores.map((s) => {
      const name    = s.name    || 'Jan Aushadhi Store';
      const address = s.address || '';
      const city    = s.city    || '';
      const state   = s.state   || '';
      const pincode = s.pincode || '';

      const locationParts = [city, state, pincode].filter(Boolean);
      const locationLine  = locationParts.length > 0
        ? locationParts.join(', ')
        : '';

      const fullAddress = [address, locationLine].filter(Boolean).join(', ');

      const distanceText = (s.distance_km !== null && s.distance_km !== undefined)
        ? `${Number(s.distance_km).toFixed(1)} km`
        : '';

      return `
        <div class="store-card">
          <div class="store-icon" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <div class="store-info">
            <div class="store-name">${escapeHtml(name)}</div>
            <div class="store-address">${escapeHtml(fullAddress)}</div>
          </div>
          ${distanceText
            ? `<span class="store-distance">${escapeHtml(distanceText)}</span>`
            : ''}
        </div>
      `;
    }).join('');

    return `
      <section class="med-section" aria-labelledby="stores-heading">
        <div class="med-section-header">
          <div>
            <h2 class="med-section-title" id="stores-heading">Nearby Jan Aushadhi</h2>
            <p class="med-section-subtitle">
              ${stores.length} ${stores.length === 1 ? 'store' : 'stores'} listed.
            </p>
          </div>
        </div>

        <div class="store-list">
          ${cards}
        </div>
      </section>
    `;
  }

  // ============================================================
  // RENDER — TRUST SUMMARY
  // ============================================================

  function renderTrust() {
    const today = new Date().toLocaleDateString('en-IN', {
      day: 'numeric', month: 'short', year: 'numeric',
    });

    return `
      <section class="med-section" aria-labelledby="trust-heading">
        <div class="trust-summary">
          <div class="trust-header">
            <div class="trust-icon" aria-hidden="true">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <div class="trust-title-block">
              <div class="trust-title" id="trust-heading">Verified Information</div>
              <div class="trust-subtitle">Last updated ${escapeHtml(today)}</div>
            </div>
          </div>

          <p class="trust-desc">
            Medicine, pricing, and generic data are sourced from
            trusted public healthcare records and cross-checked against
            official Jan Aushadhi listings.
          </p>

          <div class="trust-actions">
            <button type="button"
              class="btn btn-outline btn-sm"
              data-open-trust-passport>
              How was this verified?
            </button>
          </div>
        </div>
      </section>
    `;
  }

  // ============================================================
  // RENDER — RELATED (placeholder)
  // ============================================================

  function renderRelated() {
    return `
      <section class="med-section" aria-labelledby="related-heading">
        <div class="med-section-header">
          <div>
            <h2 class="med-section-title" id="related-heading">Related</h2>
            <p class="med-section-subtitle">Similar medicines you may consider.</p>
          </div>
        </div>

        <div class="related-list">
          <div class="related-item">
            <span class="related-item-name">Related medicines coming soon</span>
            <span class="text-caption text-muted">Future release</span>
          </div>
        </div>
      </section>
    `;
  }

  // ============================================================
  // RENDER — FULL PAGE
  // ============================================================

  function renderPage(payload, stores = []) {
    const { medicine, brands = [] } = payload;

    const avgBrand       = averageBrandPrice(brands);
    const savingsPercent = computeSavingsPercent(medicine.jan_price, avgBrand);

    els.container.innerHTML = `
      <div class="container">

        <nav class="med-breadcrumb" aria-label="Breadcrumb">
          <a class="med-breadcrumb-link" href="home.html">Home</a>
          <span class="med-breadcrumb-sep">/</span>
          <a class="med-breadcrumb-link" href="javascript:history.back()">Search</a>
          <span class="med-breadcrumb-sep">/</span>
          <span class="med-breadcrumb-current">${escapeHtml(medicine.generic_name)}</span>
        </nav>

        ${renderHero(medicine, brands, avgBrand, savingsPercent)}

        <div class="med-layout">
          <div class="med-main">
            ${renderPriceCompare(medicine, avgBrand, savingsPercent)}
            ${renderInfo(medicine)}
            ${renderBrands(brands)}
          </div>

          <aside class="med-sidebar" aria-label="Additional information">
            ${renderTrust()}
            ${renderStores(stores)}
            ${renderRelated()}
          </aside>
        </div>

      </div>
    `;
  }

  // ============================================================
  // API CALL
  // ============================================================

  async function fetchMedicine(id) {
    const url = window.AarogyaConfig.url(
      window.AarogyaConfig.endpoints.medicine(id)
    );

    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    let payload = null;
    try {
      payload = await response.json();
    } catch {
      const err = new Error('Invalid JSON');
      err.code = 'BAD_RESPONSE';
      throw err;
    }

    if (response.status === 404) {
      const err = new Error(payload?.message || 'Not found');
      err.code = 'NOT_FOUND';
      throw err;
    }

    if (!response.ok || payload?.success !== true) {
      const err = new Error(payload?.message || `HTTP ${response.status}`);
      err.code = payload?.error || `HTTP_${response.status}`;
      throw err;
    }

    if (!payload.medicine || typeof payload.medicine !== 'object') {
      const err = new Error('Malformed response');
      err.code = 'BAD_RESPONSE';
      throw err;
    }

    return payload;
  }

  // ============================================================
  // MAIN FLOW
  // ============================================================

  async function loadMedicine(id) {
    if (!id) {
      renderNotFound('No medicine identifier was provided.');
      return;
    }

    renderLoading();

    try {
      const [payload, stores] = await Promise.all([
        fetchMedicine(id),
        fetchStores(),
      ]);
      renderPage(payload, stores);
    } catch (error) {
      console.error('[Aarogya] Medicine load failed:', error);
      if (error.code === 'NOT_FOUND') {
        renderNotFound();
      } else {
        renderError(error.code || 'NETWORK_ERROR');
      }
    }
  }

  // ============================================================
  // INIT
  // ============================================================

  document.addEventListener('DOMContentLoaded', () => {
    loadMedicine(getIdFromUrl());
  });

})();
