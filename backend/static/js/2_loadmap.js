// ==========================================================================
// Map Initialization — MapTiler High-DPI Retina Vector Styles + Theme Manager
// ==========================================================================

const MAPTILER_KEY = 'DPeytGXTs5DU9As7z62J';
const KTM_CENTER = [27.700769, 85.300140];
const DEFAULT_ZOOM = 13;

// Initialize Leaflet Map
const map = L.map('map', {
  center: KTM_CENTER,
  zoom: DEFAULT_ZOOM,
  zoomControl: false,
  zoomAnimation: true,
  markerZoomAnimation: true,
  fadeAnimation: true,
  zoomSnap: 1,
  zoomDelta: 1,
  wheelPxPerZoomLevel: 100,
  bounceAtZoomLimits: false,
});

// Reposition Zoom Control cleanly to bottom right
L.control.zoom({ position: 'bottomright' }).addTo(map);

// 512px tiles cover a 2x2 block (zoomOffset -1). Do not also request @2x,
// which downloads 1024px images and makes the zoom animation snap.
const TILE_OPTS = {
  tileSize: 512,
  zoomOffset: -1,
  minZoom: 1,
  maxZoom: 19,
  detectRetina: false,
  updateWhenZooming: false,
  updateWhenIdle: false,
  keepBuffer: 4,
  updateInterval: 40,
  crossOrigin: true,
};

const maptilerStreets = L.tileLayer(
  `https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`,
  Object.assign({}, TILE_OPTS, {
    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
  })
);

const maptilerDark = L.tileLayer(
  `https://api.maptiler.com/maps/dataviz-dark/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`,
  Object.assign({}, TILE_OPTS, {
    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a>',
  })
);

let baseLayerToken = 0;

function showBaseLayer(next, prev) {
  const token = ++baseLayerToken;
  const wasReady = map.hasLayer(next) && typeof next.isLoading === 'function' && !next.isLoading();
  if (!map.hasLayer(next)) next.addTo(map);
  const dropPrev = function () {
    if (token !== baseLayerToken) return;
    if (prev && map.hasLayer(prev)) map.removeLayer(prev);
  };
  if (wasReady) {
    dropPrev();
    return;
  }
  next.once('load', dropPrev);
  setTimeout(dropPrev, 1800);
}

// ── Theme State Management with LocalStorage Persistence ──
// Default to light theme (matching the Transit App daylight screenshot)
let currentTheme = localStorage.getItem('transit_app_theme') || 'light';
let isDarkMap = (currentTheme === 'dark');
window.isDarkMap = isDarkMap;

// Add initial tile layer based on saved preference
if (isDarkMap) {
  maptilerDark.addTo(map);
  document.documentElement.classList.add('dark-theme');
} else {
  maptilerStreets.addTo(map);
  document.documentElement.classList.remove('dark-theme');
}

// Update Theme UI button icon (Sun in dark mode, Moon in light mode)
function updateThemeUI() {
  const icon = document.getElementById('mapThemeIcon');
  if (icon) {
    if (isDarkMap) {
      // Sun icon to switch to daylight
      icon.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
    } else {
      // Moon icon to switch to night mode
      icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
    }
  }

  // Notify active polylines if theme changed
  if (typeof window.applyPolylineTheme === 'function') {
    window.applyPolylineTheme(isDarkMap);
  }
}

// Toggle Theme & Persist across all route views & page reloads
function toggleMapTheme() {
  if (isDarkMap) {
    showBaseLayer(maptilerStreets, maptilerDark);
    isDarkMap = false;
    window.isDarkMap = false;
    localStorage.setItem('transit_app_theme', 'light');
    document.documentElement.classList.remove('dark-theme');
  } else {
    showBaseLayer(maptilerDark, maptilerStreets);
    isDarkMap = true;
    window.isDarkMap = true;
    localStorage.setItem('transit_app_theme', 'dark');
    document.documentElement.classList.add('dark-theme');
  }
  updateThemeUI();
}

// Recenter Map on Kathmandu
function resetMapCenter() {
  map.flyTo(KTM_CENTER, DEFAULT_ZOOM, { duration: 1.2 });
}

// Ensure theme icon reflects saved theme on load and recalculate map viewport
document.addEventListener('DOMContentLoaded', function() {
  updateThemeUI();
  setTimeout(() => {
    map.invalidateSize();
  }, 100);
});
