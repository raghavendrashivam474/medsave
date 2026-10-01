const API_BASE = window.location.origin.includes('localhost') ? 'http://localhost:5000/api' : '/api';

const searchInput = document.getElementById('searchInput');
const resultsContainer = document.getElementById('results');
const pincodeInput = document.getElementById('pincodeInput');
const findStoresBtn = document.getElementById('findStoresBtn');
const storeResults = document.getElementById('storeResults');

let debounceTimer;

// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('light-theme');
        const isLight = body.classList.contains('light-theme');
        themeToggle.innerHTML = isLight ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });
}

// Medicine Search Logic
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        
        if (query.length < 1) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon-wrap"><i class="fas fa-pills"></i></div>
                    <h3 class="empty-title">Search a branded medicine</h3>
                    <p class="empty-text">Try
                      <button type="button" class="empty-chip" data-q="Dolo">Dolo</button>
                      <button type="button" class="empty-chip" data-q="Crocin">Crocin</button>
                      <button type="button" class="empty-chip" data-q="Glycomet">Glycomet</button>
                      <button type="button" class="empty-chip" data-q="Calpol">Calpol</button>
                      to compare prices</p>
                </div>`;
            return;
        }

        resultsContainer.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Searching database...</div>';

        debounceTimer = setTimeout(() => {
            fetchMedicines(query);
        }, 300);
    });
}

async function fetchMedicines(query) {
    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        displayMedicines(data);
    } catch (error) {
        console.error('Search error:', error);
        if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="empty-state" style="color: var(--red);">Error loading medicines. Please try again.</div>';
        }
    }
}

function displayMedicines(medicines) {
    if (!resultsContainer) return;
    const list = Array.isArray(medicines) ? medicines : (medicines && medicines.data ? medicines.data : []);
    if (list.length === 0) {
        resultsContainer.innerHTML = '<div class="empty-state">
                    <div class="empty-icon-wrap"><i class="fas fa-pills"></i></div>
                    <h3 class="empty-title">Search a branded medicine</h3>
                    <p class="empty-text">Try
                      <button type="button" class="empty-chip" data-q="Dolo">Dolo</button>
                      <button type="button" class="empty-chip" data-q="Crocin">Crocin</button>
                      <button type="button" class="empty-chip" data-q="Glycomet">Glycomet</button>
                      <button type="button" class="empty-chip" data-q="Calpol">Calpol</button>
                      to compare prices</p>
                </div>';
        return;
    }

    const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

    resultsContainer.innerHTML = list.map((med) => {
        const brandPrice = Number(med.brand_price) || 0;
        const genericPrice = Number(med.generic_price) || 0;
        const packSave = Math.max(0, brandPrice - genericPrice);
        const savingsPct = med.savings_percent != null ? med.savings_percent
            : (brandPrice > 0 ? Math.round((packSave / brandPrice) * 1000) / 10 : 0);
        const matchLabel = med.match_type === 'generic' ? 'GENERIC SALT' : 'BRANDED ALTERNATIVE';
        const brandName = med.brand_name || 'Generic Medicine';
        const genericName = med.generic_name || '';
        const dosage = med.dosage || '';
        const form = med.form || '';
        const df = (dosage + ' ' + form).trim();

        return (
            '<div class="card medicine-card"' +
            ' role="button" tabindex="0"' +
            ' data-brand="' + esc(brandName) + '"' +
            ' data-generic="' + esc(genericName) + '"' +
            ' data-dosage="' + esc(dosage) + '"' +
            ' data-form="' + esc(form) + '"' +
            ' data-brand-price="' + brandPrice + '"' +
            ' data-generic-price="' + genericPrice + '">' +

            // ---- compact summary (always visible) ----
            '<div class="mc-summary">' +
              '<div class="mc-left">' +
                '<div class="mc-label">' + matchLabel + '</div>' +
                '<h3 class="mc-title">' + esc(brandName) + '</h3>' +
                '<p class="mc-generic">Generic: <strong>' + esc(genericName) + '</strong>' +
                  (df ? ' · ' + esc(df) : '') + '</p>' +
              '</div>' +
              '<div class="mc-right">' +
                '<div class="mc-brand-price">Branded: ₹' + brandPrice + '</div>' +
                '<div class="mc-generic-price">Generic: ₹' + genericPrice + '</div>' +
                '<div class="mc-save-chip">Save ' + savingsPct + '%</div>' +
              '</div>' +
            '</div>' +

            // ---- medium hover preview (revealed on hover / focus) ----
            '<div class="mc-preview" aria-hidden="true">' +
              '<div class="mc-preview-grid">' +
                '<div class="mc-preview-stat">' +
                  '<span class="mc-ps-label">Pack savings</span>' +
                  '<span class="mc-ps-value">₹' + packSave.toFixed(2) + '</span>' +
                '</div>' +
                '<div class="mc-preview-stat">' +
                  '<span class="mc-ps-label">You pay</span>' +
                  '<span class="mc-ps-value accent">₹' + genericPrice + '</span>' +
                '</div>' +
                '<div class="mc-preview-stat">' +
                  '<span class="mc-ps-label">vs branded</span>' +
                  '<span class="mc-ps-value muted"><s>₹' + brandPrice + '</s></span>' +
                '</div>' +
              '</div>' +
              '<div class="mc-preview-meta">' +
                '<span><i class="fas fa-shield-alt"></i> Jan Aushadhi certified</span>' +
                '<span><i class="fas fa-flask"></i> Same active salt</span>' +
                (df ? '<span><i class="fas fa-pills"></i> ' + esc(df) + '</span>' : '') +
              '</div>' +
              '<div class="mc-preview-cta">' +
                '<i class="fas fa-calculator"></i> Click for dose &amp; duration savings calculator' +
                '<i class="fas fa-arrow-right mc-cta-arrow"></i>' +
              '</div>' +
            '</div>' +

            '</div>'
        );
    }).join('');
}

// Store Lookup Logic
if (findStoresBtn) {
    findStoresBtn.addEventListener('click', () => {
        const pincode = pincodeInput ? pincodeInput.value.trim() : '';
        fetchStores(pincode);
    });
}

// Geolocation Support
if ("geolocation" in navigator && pincodeInput) {
    const geoBtn = document.createElement('button');
    geoBtn.innerHTML = '<i class="fas fa-location-arrow"></i> Use Location';
    geoBtn.style.cssText = "padding: 0.8rem 1rem; border-radius: 12px; background: rgba(34, 197, 94, 0.2); color: var(--accent); border: 1px solid var(--accent); cursor: pointer; font-weight: 600; font-size: 0.9rem;";
    geoBtn.onclick = () => {
        navigator.geolocation.getCurrentPosition((pos) => {
            fetchStores('', pos.coords.latitude, pos.coords.longitude);
        }, (err) => {
            alert("Unable to get location. Please enter pincode.");
        });
    };
    if (pincodeInput.parentNode) {
        pincodeInput.parentNode.appendChild(geoBtn);
    }
}

async function fetchStores(pincode = '', lat = '', lng = '') {
    const el = document.getElementById('storeResults');
    if (!el) return;
    el.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Locating stores...</div>';
    
    let json = null;
    try {
        let url = `${API_BASE}/stores`;
        const params = new URLSearchParams();
        if (pincode) params.append('pincode', pincode);
        if (lat && lng) {
            params.append('lat', lat);
            params.append('lng', lng);
        }
        if (params.toString()) url += `?${params.toString()}`;

        const response = await fetch(url);
        json = await response.json();
    } catch (error) {
        console.error('Store network/API error:', error);
        el.innerHTML = '<div class="empty-state" style="color: var(--red);">Unable to fetch stores.</div>';
        return;
    }

    try {
        displayStores(json);
    } catch (renderErr) {
        console.error('Store render error:', renderErr);
        el.innerHTML = '<div class="empty-state" style="color: var(--red);">Error displaying store data.</div>';
    }
}

function displayStores(storesInput) {
    const el = document.getElementById('storeResults');
    if (!el) return;

    let list = storesInput;
    if (!Array.isArray(list)) {
        if (list && Array.isArray(list.data)) {
            list = list.data;
        } else if (list && Array.isArray(list.stores)) {
            list = list.stores;
        } else {
            list = [];
        }
    }

    if (list.length === 0) {
        el.innerHTML = '<div class="empty-state">
                    <div class="empty-icon-wrap"><i class="fas fa-pills"></i></div>
                    <h3 class="empty-title">Search a branded medicine</h3>
                    <p class="empty-text">Try
                      <button type="button" class="empty-chip" data-q="Dolo">Dolo</button>
                      <button type="button" class="empty-chip" data-q="Crocin">Crocin</button>
                      <button type="button" class="empty-chip" data-q="Glycomet">Glycomet</button>
                      <button type="button" class="empty-chip" data-q="Calpol">Calpol</button>
                      to compare prices</p>
                </div>';
        return;
    }

    el.innerHTML = list.map(store => {
        const name = store.name || 'Jan Aushadhi Kendra';
        const address = store.address || '';
        const city = store.city || '';
        const state = store.state || '';
        const pincode = store.pincode || '';
        const lat = store.latitude || store.lat || 28.6139;
        const lng = store.longitude || store.lng || 77.2090;
        const dist = (store.distance_km !== null && store.distance_km !== undefined) ? store.distance_km : store.distance;
        const phoneHtml = store.phone ? `<div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.2rem;"><i class="fas fa-phone-alt"></i> ${store.phone}</div>` : '';
        const distHtml = (dist !== null && dist !== undefined) ? `<div style="font-size: 0.8rem; color: var(--accent); margin-top: 0.4rem; font-weight: 600;">Approx. ${Number(dist).toFixed(1)} km away</div>` : '';

        return `
        <div class="card store-card" style="margin-bottom: 1rem; padding: 1.2rem; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;">
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 0.3rem; color: var(--text-primary);">${name}</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);"><i class="fas fa-map-marker-alt"></i> ${address}${city ? ', ' + city : ''}${state ? ', ' + state : ''}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.2rem;">Pincode: ${pincode}</div>
                    ${phoneHtml}
                    ${distHtml}
                </div>
                <a href="https://www.google.com/maps?q=${lat},${lng}" target="_blank"
                   style="background: rgba(59, 130, 246, 0.2); color: var(--blue); padding: 0.5rem 0.9rem; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 0.8rem; white-space: nowrap;">
                    DIRECTIONS ↗
                </a>
            </div>
        </div>
        `;
    }).join('');
}

// Initial store load
fetchStores();

// Register Service Worker securely
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js').then(reg => {
            console.log('SW registered:', reg);
        }).catch(err => {
            console.log('SW registration failed:', err);
        });
    });
}

// ============================================
// MEDICINE DETAIL MODAL + SAVINGS CALCULATOR
// ============================================
let currentBrandPrice = 0;
let currentGenericPrice = 0;

function openMedicineModal(card) {
    const modal = document.getElementById('medicineModal');
    if (!modal) { console.error('MedSave: #medicineModal missing'); return; }

    currentBrandPrice = parseFloat(card.getAttribute('data-brand-price')) || 0;
    currentGenericPrice = parseFloat(card.getAttribute('data-generic-price')) || 0;

    const brand = card.getAttribute('data-brand') || 'Medicine';
    const generic = card.getAttribute('data-generic') || '';
    const dosage = card.getAttribute('data-dosage') || '';
    const form = card.getAttribute('data-form') || '';

    const nameEl = document.getElementById('modalBrandName');
    const subEl = document.getElementById('modalGenericName');
    const bp = document.getElementById('modalBrandPrice');
    const gp = document.getElementById('modalGenericPrice');
    const pill = document.getElementById('modalSavePill');
    const hero = document.getElementById('modalHeroSave');

    if (nameEl) nameEl.textContent = brand;

    // Clean subtitle — avoid duplicated dosage text
    if (subEl) {
        let bits = [];
        if (generic) bits.push(generic);
        const df = (dosage + ' ' + form).trim();
        if (df) bits.push(df);
        subEl.textContent = bits.length ? bits.join(' · ') : 'Generic alternative';
    }

    if (bp) bp.textContent = '₹' + formatNum(currentBrandPrice);
    if (gp) gp.textContent = '₹' + formatNum(currentGenericPrice);

    const packSave = Math.max(0, currentBrandPrice - currentGenericPrice);
    const pct = currentBrandPrice > 0 ? Math.round((packSave / currentBrandPrice) * 1000) / 10 : 0;
    if (pill) pill.textContent = 'Save ' + pct + '%';
    if (hero) hero.textContent = '₹' + formatNum(packSave);

    const u = document.getElementById('calcUnits');
    const d = document.getElementById('calcDays');
    if (u) u.value = 1;
    if (d) d.value = 30;
    setPresetActive(30);

    updateCalculator();
    modal.classList.add('active');
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
}

function closeMedicineModal() {
    const modal = document.getElementById('medicineModal');
    if (!modal) return;
    modal.classList.remove('active');
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

function formatNum(n) {
    const x = Number(n) || 0;
    return Number.isInteger(x) ? String(x) : x.toFixed(2);
}

function updateCalculator() {
    const u = document.getElementById('calcUnits');
    const d = document.getElementById('calcDays');
    const units = Math.max(0, parseFloat(u && u.value) || 0);
    const days = Math.max(0, parseFloat(d && d.value) || 0);
    const n = units * days;

    const bt = currentBrandPrice * n;
    const gt = currentGenericPrice * n;
    const sv = Math.max(0, bt - gt);
    const pct = bt > 0 ? Math.round((sv / bt) * 1000) / 10 : 0;

    const eb = document.getElementById('calcBrandTotal');
    const eg = document.getElementById('calcGenericTotal');
    const es = document.getElementById('calcTotalSavings');
    const bar = document.getElementById('savingsBarFill');
    const cap = document.getElementById('savingsBarCaption');

    if (eb) eb.textContent = '₹' + bt.toFixed(2);
    if (eg) eg.textContent = '₹' + gt.toFixed(2);
    if (es) es.textContent = '₹' + sv.toFixed(2);
    if (bar) bar.style.width = Math.min(100, pct) + '%';
    if (cap) cap.textContent = pct > 0
        ? ("You're saving " + pct + "% vs branded")
        : 'Adjust values to project savings';
}

function bumpInput(id, delta) {
    const el = document.getElementById(id);
    if (!el) return;
    const next = Math.max(1, (parseFloat(el.value) || 1) + delta);
    el.value = next;
    if (id === 'calcDays') setPresetActive(next);
    updateCalculator();
}

function setPresetActive(days) {
    document.querySelectorAll('.preset-btn').forEach(btn => {
        const d = parseInt(btn.getAttribute('data-days'), 10);
        btn.classList.toggle('active', d === days);
    });
}

// Event delegation on results
if (resultsContainer) {
    resultsContainer.addEventListener('click', function (e) {
        const card = e.target.closest('.medicine-card');
        if (card) openMedicineModal(card);
    });
    resultsContainer.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        const card = e.target.closest('.medicine-card');
        if (!card) return;
        e.preventDefault();
        openMedicineModal(card);
    });
}

(function initModalChrome() {
    const modal = document.getElementById('medicineModal');
    const closeBtn = document.getElementById('closeModal');

    if (modal) {
        modal.style.display = 'none';
        modal.addEventListener('click', function (e) {
            if (e.target === modal) closeMedicineModal();
        });
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            closeMedicineModal();
        });
    }
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeMedicineModal();
    });

    const u = document.getElementById('calcUnits');
    const d = document.getElementById('calcDays');
    if (u) u.addEventListener('input', updateCalculator);
    if (d) d.addEventListener('input', function () {
        setPresetActive(parseInt(d.value, 10));
        updateCalculator();
    });

    const bind = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener('click', fn); };
    bind('unitsMinus', function () { bumpInput('calcUnits', -1); });
    bind('unitsPlus',  function () { bumpInput('calcUnits', +1); });
    bind('daysMinus',  function () { bumpInput('calcDays', -1); });
    bind('daysPlus',   function () { bumpInput('calcDays', +1); });

    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const days = parseInt(btn.getAttribute('data-days'), 10) || 30;
            const dEl = document.getElementById('calcDays');
            if (dEl) dEl.value = days;
            setPresetActive(days);
            updateCalculator();
        });
    });

    console.log('MedSave: premium modal ready =', !!modal);
})();

// Empty-state quick search chips
document.addEventListener('click', function (e) {
    const chip = e.target.closest('.empty-chip');
    if (!chip) return;
    const q = chip.getAttribute('data-q');
    if (!q || !searchInput) return;
    searchInput.value = q;
    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    searchInput.focus();
});

// Place geolocation button into designed slot (override old append)
(function refineGeoBtn() {
    if (!("geolocation" in navigator)) return;
    const slot = document.getElementById('geoBtnSlot');
    const bar = document.getElementById('storeSearchBar');
    // Remove any old injected geo buttons that were appended earlier
    if (bar) {
        bar.querySelectorAll('button').forEach(b => {
            if (b.id !== 'findStoresBtn' && b.id !== 'geoBtnSlot' && /location/i.test(b.textContent || '')) {
                b.remove();
            }
        });
    }
    let geoBtn = slot;
    if (!geoBtn) return;
    geoBtn.hidden = false;
    geoBtn.className = 'btn btn-ghost';
    geoBtn.type = 'button';
    geoBtn.innerHTML = '<i class="fas fa-location-arrow"></i> Use Location';
    geoBtn.onclick = function () {
        geoBtn.disabled = true;
        geoBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating...';
        navigator.geolocation.getCurrentPosition(function (pos) {
            fetchStores('', pos.coords.latitude, pos.coords.longitude);
            geoBtn.disabled = false;
            geoBtn.innerHTML = '<i class="fas fa-location-arrow"></i> Use Location';
        }, function () {
            alert('Unable to get location. Please enter pincode.');
            geoBtn.disabled = false;
            geoBtn.innerHTML = '<i class="fas fa-location-arrow"></i> Use Location';
        });
    };
})();


