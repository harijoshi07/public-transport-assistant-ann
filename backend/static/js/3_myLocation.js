// Create a green marker with an initial position [0, 0]
var marker = L.marker([0, 0], {
    icon: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
        iconSize: [15, 27],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    })
}).addTo(map);
 
function updateMarkerLocation(location) {
    marker.setLatLng(location);
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                var latitude = position.coords.latitude;
                var longitude = position.coords.longitude;
                var location = [latitude, longitude];
                updateMarkerLocation(location);
            },
            function(error) {
                console.error('Error getting location:', error.message);
            }
        );
    } else {
        console.error('Geolocation is not supported by this browser.');
    }
}

// Get and update the location every 0.1 seconds (you can adjust the interval as needed)
setInterval(getLocation, 100);


// Initial location update
getLocation();


// Function to show a popup saying "My Location"
function showLocationPopup() {
    if (!marker.isPopupOpen()) {
        marker.bindPopup("My Location").openPopup();
    }
}

// Event listener to show popup on marker click
marker.on('click', showLocationPopup);















