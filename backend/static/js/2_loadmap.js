// Leaflet Map Initialization centered on Kathmandu Valley
const key = 'DPeytGXTs5DU9As7z62J';

// Default center: Kathmandu, Nepal
const map = L.map('map').setView([27.700769, 85.300140], 13);

// Base tile layer with MapTiler and OpenStreetMap fallback
try {
  L.maptilerLayer({
    apiKey: key,
    style: "f333b8a3-3867-44c9-8695-f2d1dd7f5dea",
  }).addTo(map);
} catch (e) {
  console.warn("MapTiler unavailable, falling back to OpenStreetMap tiles:", e);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
}

// Safely attach search input if element exists in the template
document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('search-input');
  if (searchInput && typeof GraphHopper !== 'undefined') {
    try {
      const ghGeocoding = new GraphHopper.Geocoding({
        key: '8e95a1e4-6d07-488c-8f23-d95874da0c18',
      });

      searchInput.addEventListener('input', function (event) {
        const query = event.target.value.trim();
        ghGeocoding.clear();

        if (query.length >= 3) {
          ghGeocoding.geocode(query, function (result) {
            if (result && result.hits && result.hits.length > 0) {
              const location = result.hits[0].point;
              map.setView([location.lat, location.lng], 14);
            }
          });
        }
      });
    } catch (err) {
      console.warn('Geocoding setup skipped:', err);
    }
  }
});
