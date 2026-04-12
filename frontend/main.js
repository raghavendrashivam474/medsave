const API_BASE = 'https://medsave-bqf3.onrender.com';

const searchInput = document.getElementById('searchInput');
const resultsContainer = document.getElementById('results');
const pincodeInput = document.getElementById('pincodeInput');
const findStoresBtn = document.getElementById('findStoresBtn');
const storeResults = document.getElementById('storeResults');

let debounceTimer;

// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

themeToggle.addEventListener('click', () => {
    body.classList.toggle('light-theme');
    const isLight = body.classList.contains('light-theme');
    themeToggle.innerHTML = isLight ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
});

// Medicine Search Logic
searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const query = e.target.value.trim();
    
    if (query.length < 2) {
        if (query.length === 0) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-pills" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>Enter a medicine name to start comparing prices</p>
                </div>
            `;
        }
        return;
    }

    debounceTimer = setTimeout(() => {
        performSearch(query);
    }, 400);
});

async function performSearch(query) {
    resultsContainer.innerHTML = '<div class="loading">Searching verified database...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        displayResults(data);
    } catch (error) {
        console.error('Search failed:', error);
        resultsContainer.innerHTML = '<div class="empty-state" style="color: var(--red);">API Connection failed. Please check if the backend is running.</div>';
    }
}

function displayResults(results) {
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="empty-state">No matching medicines found. Try another name.</div>';
        return;
    }

    resultsContainer.innerHTML = results.map((item, index) => `
        <div class="card" style="animation-delay: ${index * 0.1}s" id="med-${index}">
            <div class="card-header">
                <div>
                    <div class="brand-name">${item.brand_name}</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);">${item.form} • ${item.dosage}</div>
                </div>
                <div class="savings-badge">SAVE ${item.savings_percent}%</div>
            </div>
            
            <div class="card-body">
                <div class="info-group">
                    <label>Salt / Composition</label>
                    <span>${item.salt}</span>
                </div>
                <div class="info-group">
                    <label>Generic Alternative</label>
                    <span class="generic-highlight">${item.generic_name}</span>
                </div>
            </div>

            <div class="chart-container">
                <canvas id="chart-${index}"></canvas>
            </div>

            <div class="price-comparison">
                <div class="price-box">
                    <div class="price-label">BRANDED PRICE</div>
                    <div class="price-val" style="color: var(--text-secondary);">₹${item.brand_price}</div>
                </div>
                <div style="font-size: 1.5rem; color: var(--text-secondary); opacity: 0.3;">
                    <i class="fas fa-chevron-right"></i>
                </div>
                <div class="price-box">
                    <div class="price-label">GENERIC PRICE</div>
                    <div class="price-val" style="color: var(--accent);">₹${item.generic_price}</div>
                </div>
                <div class="price-box">
                    <div class="price-label">YOUR SAVINGS</div>
                    <div class="save-amount">₹${(item.brand_price - item.generic_price).toFixed(1)}</div>
                </div>
            </div>

            <button class="calculator-toggle" onclick="toggleCalculator(${index})">
                <i class="fas fa-calculator"></i> Calculate My Monthly Savings
            </button>

            <div class="calculator-panel" id="calc-panel-${index}">
                <div class="calc-grid">
                    <div class="calc-input-group">
                        <label>Tablets per day</label>
                        <input type="number" value="1" min="1" oninput="updateCalculation(${index}, ${item.brand_price}, ${item.generic_price})">
                    </div>
                    <div class="calc-input-group">
                        <label>Days per month</label>
                        <input type="number" value="30" min="1" oninput="updateCalculation(${index}, ${item.brand_price}, ${item.generic_price})">
                    </div>
                    <div class="calc-result">
                        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.2rem;">ESTIMATED MONTHLY SAVINGS</div>
                        <div class="big-save" id="calc-save-${index}">₹${((item.brand_price - item.generic_price) * 3).toFixed(1)}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 1rem; font-size: 0.8rem; color: var(--accent);">
                <i class="fas fa-check-circle"></i> Equivalent to Jan Aushadhi standards
            </div>
        </div>
    `).join('');

    // Initialize Charts
    results.forEach((item, index) => {
        initChart(index, item.brand_name, item.brand_price, item.generic_name, item.generic_price);
    });
}

function initChart(index, brandLabel, brandPrice, genericLabel, genericPrice) {
    const ctx = document.getElementById(`chart-${index}`).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Branded', 'Generic'],
            datasets: [{
                data: [brandPrice, genericPrice],
                backgroundColor: [
                    'rgba(148, 163, 184, 0.4)', // Slate
                    'rgba(34, 197, 94, 0.6)'    // Accent
                ],
                borderColor: [
                    'rgba(148, 163, 184, 1)',
                    'rgba(34, 197, 94, 1)'
                ],
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#f8fafc' }
                }
            }
        }
    });
}

window.toggleCalculator = (index) => {
    const panel = document.getElementById(`calc-panel-${index}`);
    panel.classList.toggle('active');
};

window.updateCalculation = (index, brandPrice, genericPrice) => {
    const panels = document.getElementById(`calc-panel-${index}`);
    const inputs = panels.querySelectorAll('input');
    const daily = parseFloat(inputs[0].value) || 0;
    const days = parseFloat(inputs[1].value) || 0;
    
    // Assuming brandPrice/genericPrice is for a pack of 10 for simplicity in this demo calculation
    // Let's assume price is per unit for now.
    const unitSav = brandPrice - genericPrice;
    const monthlySav = daily * days * unitSav;
    
    document.getElementById(`calc-save-${index}`).innerText = `₹${monthlySav.toFixed(1)}`;
};

// Store Lookup Logic
findStoresBtn.addEventListener('click', () => {
    const pincode = pincodeInput.value.trim();
    fetchStores(pincode);
});

// Geolocation Support
if ("geolocation" in navigator) {
    const geoBtn = document.createElement('button');
    geoBtn.innerHTML = '<i class="fas fa-location-arrow"></i> Use Location';
    geoBtn.style.cssText = "padding: 0.8rem; border-radius: 12px; background: rgba(34, 197, 94, 0.2); color: var(--accent); border: 1px solid var(--accent); cursor: pointer; font-weight: 600;";
    geoBtn.onclick = () => {
        navigator.geolocation.getCurrentPosition((pos) => {
            fetchStores('', pos.coords.latitude, pos.coords.longitude);
        }, (err) => {
            alert("Unable to get location. Please enter pincode.");
        });
    };
    pincodeInput.parentNode.appendChild(geoBtn);
}

async function fetchStores(pincode = '', lat = '', lng = '') {
    storeResults.innerHTML = '<div class="loading">Locating stores...</div>';
    
    try {
        let url = `${API_BASE}/stores?pincode=${pincode}`;
        if (lat && lng) url += `&lat=${lat}&lng=${lng}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        displayStores(data);
    } catch (error) {
        console.error('Store fetch failed:', error);
        storeResults.innerHTML = '<div class="empty-state" style="color: var(--red);">Unable to fetch stores.</div>';
    }
}

function displayStores(stores) {
    if (stores.length === 0) {
        storeResults.innerHTML = '<div class="empty-state">No stores found.</div>';
        return;
    }

    storeResults.innerHTML = stores.map(store => `
        <div class="card store-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 0.3rem;">${store.name}</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);"><i class="fas fa-map-marker-alt"></i> ${store.address}, ${store.city}</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.3rem;">Pincode: ${store.pincode}</div>
                    ${store.distance ? `<div style="font-size: 0.8rem; color: var(--accent); margin-top: 0.5rem; font-weight: 600;">Approx. ${store.distance.toFixed(1)} km away</div>` : ''}
                </div>
                <a href="https://www.google.com/maps?q=${store.lat},${store.lng}" target="_blank" 
                   style="background: rgba(59, 130, 246, 0.2); color: var(--blue); padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.8rem;">
                    DIRECTIONS
                </a>
            </div>
        </div>
    `).join('');
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
