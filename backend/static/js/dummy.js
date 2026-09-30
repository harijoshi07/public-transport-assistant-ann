const myLoc = JSON.parse(document.getElementById('myLoc').textContent);
const nearestMyLoc = JSON.parse(document.getElementById('nearestMyLoc').textContent);
const nearestDestLoc = JSON.parse(document.getElementById('nearestDestLoc').textContent);
const destLoc = JSON.parse(document.getElementById('destLoc').textContent);


// Create routing control with custom style for dotted line
L.Routing.control({
    router: L.Routing.graphHopper('8e95a1e4-6d07-488c-8f23-d95874da0c18'),
    waypoints: [
        L.latLng(myLoc),
        L.latLng(nearestMyLoc),
    ],
    routeWhileDragging: true,
    addWaypoints: false,
    draggableWaypoints: false,
    lineOptions: {
        styles: [{color: 'grey', opacity: 0.9, dashArray: '12, 12'}], // Set the dash pattern for a dotted line
    },
    show: false,
    //profile: 'foot', // Specify the profile for walking
    //profile:'bike',
}).addTo(map);

// Add markers for myLoc and destLoc
L.marker(myLoc).addTo(map).bindPopup('Source Location');
L.marker(nearestMyLoc).addTo(map).bindPopup('Source Nearest Location');



L.Routing.control({
    router: L.Routing.graphHopper('8e95a1e4-6d07-488c-8f23-d95874da0c18'),
    waypoints: [
        L.latLng(nearestMyLoc),
        L.latLng(nearestDestLoc),
    ],
    routeWhileDragging: true,
    addWaypoints: false,
    draggableWaypoints: false,
    lineOptions: {
        styles: [{color: 'green', opacity: 0.9}], // Set the dash pattern for a dotted line
    },
    show: false,
    //profile: 'foot', // Specify the profile for walking
    //profile:'bike',
}).addTo(map);

// Add markers for myLoc and destLoc
L.marker(nearestMyLoc).addTo(map).bindPopup('Source Nearest Location');
L.marker(nearestDestLoc).addTo(map).bindPopup('Destination Nearest Location');



// Create routing control with custom style for dotted line
L.Routing.control({
    router: L.Routing.graphHopper('8e95a1e4-6d07-488c-8f23-d95874da0c18'),
    waypoints: [
        L.latLng(nearestDestLoc),
        L.latLng(destLoc),
    ],
    routeWhileDragging: true,
    addWaypoints: false,
    draggableWaypoints: false,
    lineOptions: {
        styles: [{color: 'grey', opacity: 0.9, dashArray: '12, 12'}] // Set the dash pattern for a dotted line
    },
    show: false,
    //profile: 'foot', // Specify the profile for walking
    // profile:'bike'
}).addTo(map);

// Add markers for myLoc and destLoc
L.marker(nearestDestLoc).addTo(map).bindPopup('DEstination Nearest Location');
L.marker(destLoc).addTo(map).bindPopup('Destination Location');

