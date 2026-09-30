import re

with open('./frontend/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace fetchStores and displayStores with clean, envelope-aware logic
pattern = r"async function fetchStores\(.*?\n}\n\nfunction displayStores\(.*?\n}"

replacement = """async function fetchStores(pincode = '', lat = '', lng = '') {
    const storeResults = document.getElementById('storeResults');
    if (!storeResults) return;
    storeResults.innerHTML = '<div class="loading">Locating stores...</div>';
    
    try {
        let url = `${API_BASE}/stores?pincode=${pincode}`;
        if (lat && lng) url = `${API_BASE}/stores?lat=${lat}&lng=${lng}`;
        
        const response = await fetch(url);
        const json = await response.json();
        
        const storesList = Array.isArray(json) ? json : (json.data || []);
        displayStores(storesList);
    } catch (error) {
        console.error('Store fetch failed:', error);
        storeResults.innerHTML = '<div class="empty-state" style="color: var(--red);">Unable to fetch stores.</div>';
    }
}

function displayStores(stores) {
    const storeResults = document.getElementById('storeResults');
    if (!storeResults) return;

    if (!Array.isArray(stores) || stores.length === 0) {
        storeResults.innerHTML = '<div class="empty-state">No Jan Aushadhi Kendras found for this query.</div>';
        return;
    }

    storeResults.innerHTML = stores.map(store => {
        const lat = store.latitude || store.lat || 28.6139;
        const lng = store.longitude || store.lng || 77.2090;
        const dist = store.distance_km || store.distance;
        const phone = store.phone ? `<div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.2rem;"><i class="fas fa-phone-alt"></i> ${store.phone}</div>` : '';

        return `
        <div class="card store-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;">
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 0.3rem;">${store.name}</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);"><i class="fas fa-map-marker-alt"></i> ${store.address}, ${store.city}, ${store.state || ''}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.2rem;">Pincode: ${store.pincode}</div>
                    ${phone}
                    ${dist ? `<div style="font-size: 0.8rem; color: var(--accent); margin-top: 0.4rem; font-weight: 600;">Approx. ${Number(dist).toFixed(1)} km away</div>` : ''}
                </div>
                <a href="https://www.google.com/maps?q=${lat},${lng}" target="_blank"
                   style="background: rgba(59, 130, 246, 0.2); color: var(--blue); padding: 0.5rem 0.8rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.8rem; white-space: nowrap;">
                    DIRECTIONS ↗
                </a>
            </div>
        </div>
        `;
    }).join('');
}"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('./frontend/main.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[✓] Patched frontend/main.js successfully.")
