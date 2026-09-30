// ==========================================================================
// Map Initialization — CartoDB Voyager / Dark Matter (Transit App style)
// ==========================================================================

// Kathmandu Valley Center Coordinates
const KTM_CENTER = [27.700769, 85.300140];
const DEFAULT_ZOOM = 13;

// Initialize Leaflet Map
const map = L.map('map', {
  center: KTM_CENTER,
  zoom: DEFAULT_ZOOM,
  zoomControl: false, // Repositioned cleanly
});

// Clean Top-Right Zoom Control
L.control.zoom({ position: 'bottomright' }).addTo(map);

// ── Tile Layers ──
// CartoDB Voyager (Default crisp transit basemap)
const voyagerLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
  maxZoom: 19,
  subdomains: 'abcd',
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
});

// CartoDB Dark Matter (Night transit basemap)
const darkMatterLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  maxZoom: 19,
  subdomains: 'abcd',
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
});

// Load Default Voyager Layer
voyagerLayer.addTo(map);
let isDarkMap = false;

// Function to Toggle Map Theme (called from floating map controls)
function toggleMapTheme() {
  const icon = document.getElementById('mapThemeIcon');
  if (isDarkMap) {
    map.removeLayer(darkMatterLayer);
    map.addLayer(voyagerLayer);
    isDarkMap = false;
    if (icon) icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
  } else {
    map.removeLayer(voyagerLayer);
    map.addLayer(darkMatterLayer);
    isDarkMap = true;
    if (icon) icon.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
  }
}

// Center to Kathmandu
function resetMapCenter() {
  map.flyTo(KTM_CENTER, DEFAULT_ZOOM, { duration: 1.2 });
}
