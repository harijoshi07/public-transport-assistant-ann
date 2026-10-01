// ==========================================================================
// Map Initialization — MapTiler High-DPI Retina Vector Styles
// ==========================================================================

const MAPTILER_KEY = 'DPeytGXTs5DU9As7z62J';
const KTM_CENTER = [27.700769, 85.300140];
const DEFAULT_ZOOM = 13;

// Initialize Leaflet Map with smooth zoom animations
const map = L.map('map', {
  center: KTM_CENTER,
  zoom: DEFAULT_ZOOM,
  zoomControl: false,
  fadeAnimation: true,
});

// Reposition Zoom Control cleanly to bottom right
L.control.zoom({ position: 'bottomright' }).addTo(map);

// ── MapTiler High-DPI (@2x Retina) Tile Layers ──
// 1. MapTiler Streets-v2 (Crisp, High-Detail Daylight Basemap)
const maptilerStreets = L.tileLayer(
  `https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}@2x.png?key=${MAPTILER_KEY}`,
  {
    tileSize: 512,
    zoomOffset: -1,
    minZoom: 1,
    maxZoom: 19,
    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
    crossOrigin: true,
  }
);

// 2. MapTiler Dataviz Dark (Sleek High-Contrast Night Basemap)
const maptilerDark = L.tileLayer(
  `https://api.maptiler.com/maps/dataviz-dark/{z}/{x}/{y}@2x.png?key=${MAPTILER_KEY}`,
  {
    tileSize: 512,
    zoomOffset: -1,
    minZoom: 1,
    maxZoom: 19,
    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a>',
    crossOrigin: true,
  }
);

// Add Default MapTiler Streets Layer
maptilerStreets.addTo(map);
let isDarkMap = false;

// Theme Toggle Function (flips between MapTiler Streets-v2 and Dataviz Dark)
function toggleMapTheme() {
  const icon = document.getElementById('mapThemeIcon');
  if (isDarkMap) {
    map.removeLayer(maptilerDark);
    map.addLayer(maptilerStreets);
    isDarkMap = false;
    if (icon) {
      icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
    }
  } else {
    map.removeLayer(maptilerStreets);
    map.addLayer(maptilerDark);
    isDarkMap = true;
    if (icon) {
      icon.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
    }
  }
}

// Smooth Fly-to Kathmandu Center
function resetMapCenter() {
  map.flyTo(KTM_CENTER, DEFAULT_ZOOM, { duration: 1.2 });
}
