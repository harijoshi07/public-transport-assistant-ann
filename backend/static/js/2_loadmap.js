    // Leaflet Map 
    const key = 'DPeytGXTs5DU9As7z62J';

    const map = L.map('map').setView([27.6938263, 85.3213987], 15);

    const mtLayer = L.maptilerLayer({
    apiKey: key,
    style: "f333b8a3-3867-44c9-8695-f2d1dd7f5dea", //optional
    }).addTo(map); 

    // const geocoderControl = L.control.maptilerGeocoding({
    //     apiKey: key,
    //     country: 'Nepal'
    // }).addTo(map);


    // Set up GraphHopper
    const ghGeocoding = new GraphHopper.Geocoding({
            key: '8e95a1e4-6d07-488c-8f23-d95874da0c18',
        });

        document.getElementById('search-input').addEventListener('input', function (event) {
            const query = event.target.value;

            // Clear previous results
            ghGeocoding.clear();

            if (query.length >= 3) {
                // Perform geocoding
                ghGeocoding.geocode(query, function (result) {
                    if (result && result.hits && result.hits.length > 0) {
                        const location = result.hits[0].point;
                        map.setView([location.lat, location.lng], 13);
                    }
                });
            }
        });



        