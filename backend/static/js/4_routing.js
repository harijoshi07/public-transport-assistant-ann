const myLoc = JSON.parse(document.getElementById('myLoc').textContent);
const nearestMyLoc = JSON.parse(document.getElementById('nearestMyLoc').textContent);
const nearestDestLoc = JSON.parse(document.getElementById('nearestDestLoc').textContent);
const destLoc = JSON.parse(document.getElementById('destLoc').textContent);

 
// Create routing control for foot profile (myLoc to nearestMyLoc)
L.Routing.control({
    router: L.Routing.graphHopper('8e95a1e4-6d07-488c-8f23-d95874da0c18'),
    waypoints: [
        L.latLng(myLoc),
        L.latLng(destLoc),
    ],
    routeWhileDragging: true,
    addWaypoints: false,
    draggableWaypoints: false,
    lineOptions: {
        styles: [{color: 'blue', opacity: 0.9, width: 2}], // Set the dash pattern for a dotted line
    },
    show:true,
    profile:'bike',
}).addTo(map);

// Add markers for myLoc and destLoc
L.marker(myLoc).addTo(map).bindPopup('Source Location');
L.marker(destLoc).addTo(map).bindPopup('Destination Location');























