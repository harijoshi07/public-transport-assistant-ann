// Routing Handler between Origin, Nearest Stations, and Destination

document.addEventListener('DOMContentLoaded', function () {
  try {
    const myLocEl = document.getElementById('myLoc');
    const destLocEl = document.getElementById('destLoc');
    const nearestMyLocEl = document.getElementById('nearestMyLoc');
    const nearestDestLocEl = document.getElementById('nearestDestLoc');

    const myLoc = (myLocEl && myLocEl.textContent.trim() !== 'null') ? JSON.parse(myLocEl.textContent) : null;
    const destLoc = (destLocEl && destLocEl.textContent.trim() !== 'null') ? JSON.parse(destLocEl.textContent) : null;
    const nearestMyLoc = (nearestMyLocEl && nearestMyLocEl.textContent.trim() !== 'null') ? JSON.parse(nearestMyLocEl.textContent) : null;
    const nearestDestLoc = (nearestDestLocEl && nearestDestLocEl.textContent.trim() !== 'null') ? JSON.parse(nearestDestLocEl.textContent) : null;

    if (myLoc && destLoc && Array.isArray(myLoc) && Array.isArray(destLoc)) {
      // Add custom icons for source and destination
      const greenIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
      });

      const redIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
      });

      const busIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
      });

      // Markers for User Source and Destination
      L.marker(myLoc, { icon: greenIcon }).addTo(map).bindPopup('<b>Origin</b><br>Your Location').openPopup();
      L.marker(destLoc, { icon: redIcon }).addTo(map).bindPopup('<b>Destination</b><br>Dropoff Point');

      // Nearest Transit Stop Markers if available
      if (nearestMyLoc && Array.isArray(nearestMyLoc)) {
        L.marker(nearestMyLoc, { icon: busIcon }).addTo(map).bindPopup('<b>Nearest Boarding Stop</b>');
      }
      if (nearestDestLoc && Array.isArray(nearestDestLoc)) {
        L.marker(nearestDestLoc, { icon: busIcon }).addTo(map).bindPopup('<b>Nearest Alighting Stop</b>');
      }

      // Graphhopper Routing Control
      if (typeof L.Routing !== 'undefined' && typeof L.Routing.graphHopper !== 'undefined') {
        try {
          L.Routing.control({
            router: L.Routing.graphHopper('8e95a1e4-6d07-488c-8f23-d95874da0c18'),
            waypoints: [
              L.latLng(myLoc[0], myLoc[1]),
              L.latLng(destLoc[0], destLoc[1])
            ],
            routeWhileDragging: false,
            addWaypoints: false,
            draggableWaypoints: false,
            lineOptions: {
              styles: [{ color: '#2563EB', opacity: 0.85, weight: 5 }]
            },
            show: true
          }).addTo(map);
        } catch (routerErr) {
          console.warn('GraphHopper routing failed, drawing fallback route line:', routerErr);
          L.polyline([myLoc, destLoc], { color: '#2563EB', weight: 4, dashArray: '6, 8' }).addTo(map);
        }
      } else {
        // Fallback straight-line corridor
        L.polyline([myLoc, destLoc], { color: '#2563EB', weight: 4, dashArray: '6, 8' }).addTo(map);
      }

      // Fit map view to encompass both points
      map.fitBounds([myLoc, destLoc], { padding: [60, 60] });
    }
  } catch (err) {
    console.error('Error initializing map routing:', err);
  }
});
