//Create a routing between UserLocation and destination location that came from form submission


// var marker = L.marker([0, 0], {
//     icon: L.icon({
//         iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
//         iconSize: [15, 27],
//         iconAnchor: [12, 41],
//         popupAnchor: [1, -34],
//         shadowSize: [41, 41]
//     })
// }).addTo(map);

// var srcLat = null;
// var srcLng = null;
// var destLat = null;
// var destLng = null;

 
// function updateMarkerLocation(location) {
//     marker.setLatLng(location);
// }

// function getLocation() {
//     if (navigator.geolocation) {
//         navigator.geolocation.getCurrentPosition(
//             function(position) {
//                 var latitude = position.coords.latitude;
//                 srcLat = latitude;

//                 var longitude = position.coords.longitude;
//                 srcLng = longitude;

//                 var location = [latitude, longitude];
//                 updateMarkerLocation(location);
                
//             },
//             function(error) {
//                 console.error('Error getting location:', error.message);
//             }
//         );
//     } else {
//         console.error('Geolocation is not supported by this browser.');
//     }
// }

// // Get and update the location every 1 seconds (you can adjust the interval as needed)
// setInterval(getLocation, 100);

// // Initial location update
// getLocation();

// // Function to show a popup saying "My Location"
// function showLocationPopup() {
//     if (!marker.isPopupOpen()) {
//         marker.bindPopup("My Location").openPopup();
//     }
// }

// // Event listener to show popup on marker click
// marker.on('click', showLocationPopup);




document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('destination-location');
    const suggestionsList = document.getElementById('suggestions');

    // Function to make a request to the GraphHopper API and get location suggestions
    async function getLocationSuggestions(query) {
        const apiKey = '8e95a1e4-6d07-488c-8f23-d95874da0c18';
        const endpoint = 'https://graphhopper.com/api/1/geocode';

        const response = await fetch(`${endpoint}?q=${query}&key=${apiKey}`);
        const data = await response.json();

        const nepalSuggestions = data.hits.filter(hit => hit.countrycode === 'NP');

        return nepalSuggestions.map(hit => hit.name);
    }

    // Function to update the suggestions list based on user input
    async function updateSuggestions() {
        const query = searchInput.value.trim();

        if (query.length === 0) {
            suggestionsList.style.display = 'none';
            return;
        }

        const suggestions = await getLocationSuggestions(query);

        if (suggestions.length > 0) {
            suggestionsList.innerHTML = suggestions.map(suggestion => `<li>${suggestion}</li>`).join('');
            suggestionsList.style.display = 'block';
        } else {
            suggestionsList.style.display = 'none';
        }
    }

    // Event listener for input changes
    searchInput.addEventListener('input', updateSuggestions);

    // Event listener to handle suggestion selection
    suggestionsList.addEventListener('click', (event) => {
        if (event.target.tagName === 'LI') {
            searchInput.value = event.target.textContent;
            suggestionsList.style.display = 'none';
            // dest = searchInput.value;
            
            // // Use geocoding to get latitude and longitude for dest
            // const geocodeResult = getGeocode(dest);
            
            // if (geocodeResult) {
            //     // Assuming the geocoding result provides latitude and longitude properties
            //     const { lat, lng } = geocodeResult;
            //     destLat = lat;
            //     destLng = lng;

            //     // Store the latitude and longitude in destLoc
            //     destLoc = [lat, lng];
            //     handleRouting( srcLat, srcLng ,destLat, destLoc);
            // }            
        }
        
    });
    
  });









