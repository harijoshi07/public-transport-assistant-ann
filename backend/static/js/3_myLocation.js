// User Location Marker on Leaflet Map
let userMarker = null;

function updateMarkerLocation(lat, lng) {
  if (!userMarker) {
    userMarker = L.marker([lat, lng], {
      icon: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      })
    }).addTo(map);
    userMarker.bindPopup("<b>Your Current GPS Location</b>");
  } else {
    userMarker.setLatLng([lat, lng]);
  }
}

function getUserLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (position) {
        updateMarkerLocation(position.coords.latitude, position.coords.longitude);
      },
      function (error) {
        // Silently log without alert/freezing the user interface
        console.log('Geolocation not permitted or unavailable:', error.message);
      },
      { timeout: 10000, maximumAge: 30000 }
    );
  }
}

// Request position on load and check periodically every 15 seconds
document.addEventListener('DOMContentLoaded', function () {
  getUserLocation();
  setInterval(getUserLocation, 15000);
});
