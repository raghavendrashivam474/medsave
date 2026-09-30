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
                    <i class="fas fa-pills" style="font-size: 2.5rem; margin-bottom: 1rem; color: var(--text-secondary);"></i>
                    <p>Enter a medicine name to start comparing prices</p>
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
        resultsContainer.innerHTML = '<div class="empty-state">No matching medicines found. Try searching for "Paracetamol", "Atorvastatin", or "Metformin".</div>';
        return;
    }

    resultsContainer.innerHTML = list.map(med => {
        const savings = (med.brand_price && med.generic_price) ? (med.brand_price - med.generic_price).toFixed(2) : '0.00';
        return `
        <div class="card medicine-card" style="margin-bottom: 1.5rem; padding: 1.5rem; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); font-weight: 700; margin-bottom: 0.3rem;">
                        ${med.match_type === 'generic' ? 'GENERIC SALT' : 'BRANDED ALTERNATIVE'}
                    </div>
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.2rem;">${med.brand_name || 'Generic Medicine'}</h3>
                    <p style="font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Generic: <strong>${med.generic_name || ''}</strong> (${med.dosage || ''} ${med.form || ''})</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.85rem; color: var(--text-secondary); text-decoration: line-through;">Branded: ₹${med.brand_price || 0}</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: var(--accent);">Generic: ₹${med.generic_price || 0}</div>
                    <div style="font-size: 0.85rem; color: #22c55e; font-weight: 700; margin-top: 0.2rem;">Save ${med.savings_percent || 0}% (₹${savings})</div>
                </div>
            </div>
        </div>
        `;
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

    // Ultra-defensive extraction: handles raw array, {data: [...]}, {stores: [...]}, or raw object
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
        el.innerHTML = '<div class="empty-state">No Jan Aushadhi Kendras found for this query.</div>';
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

// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js').then(reg => {
            console.log('SW registered:', reg);
        }).catch(err => {
            console.log('SW registration failed:', err);
        });
    });
}
