// ==========================================================================
// Street-Accurate Routing Engine (OSRM) — Matches Transit App Screenshot
// ==========================================================================

let activeTransitPolyline = null;
let activeWalkPolyline1 = null;
let activeWalkPolyline2 = null;

function transitPinIcon(fill) {
  const html = `
    <div style="filter: drop-shadow(0 4px 10px rgba(0,0,0,0.35)); cursor: pointer;">
      <svg width="32" height="42" viewBox="0 0 24 32" fill="none">
        <path d="M12 0C5.37 0 0 5.37 0 12C0 22 12 32 12 32C12 32 24 22 24 12C24 5.37 18.63 0 12 0Z" fill="${fill}"/>
        <circle cx="12" cy="11" r="5" fill="#FFFFFF"/>
        <circle cx="12" cy="11" r="2.5" fill="${fill}"/>
      </svg>
    </div>`;
  return L.divIcon({
    html: html,
    className: '',
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -38]
  });
}
window.transitPinIcon = transitPinIcon;

function routeTimeIcon(minutes) {
  return L.divIcon({
    className: 'route-time-marker',
    html: '<div class="route-time-tag"><b>' + minutes + '</b><small>min</small></div>',
    iconSize: [68, 28],
    iconAnchor: [34, 34]
  });
}

document.addEventListener('DOMContentLoaded', async function () {
  const locateAtStart = window.userLocateSeq || 0;
  try {
    const myLocEl = document.getElementById('myLoc');
    const destLocEl = document.getElementById('destLoc');
    const nearestMyLocEl = document.getElementById('nearestMyLoc');
    const nearestDestLocEl = document.getElementById('nearestDestLoc');

    const myLoc = (myLocEl && myLocEl.textContent.trim() !== 'null') ? JSON.parse(myLocEl.textContent) : null;
    const destLoc = (destLocEl && destLocEl.textContent.trim() !== 'null') ? JSON.parse(destLocEl.textContent) : null;
    const nearestMyLoc = (nearestMyLocEl && nearestMyLocEl.textContent.trim() !== 'null') ? JSON.parse(nearestMyLocEl.textContent) : null;
    const nearestDestLoc = (nearestDestLocEl && nearestDestLocEl.textContent.trim() !== 'null') ? JSON.parse(nearestDestLocEl.textContent) : null;

    window.planTripSelected = !!(myLoc && destLoc && Array.isArray(myLoc) && Array.isArray(destLoc));

    if (window.planTripSelected) {
      L.marker(myLoc, { icon: transitPinIcon('#00B377') }).addTo(map).bindPopup('<b>Starting Location</b>');
      L.marker(destLoc, { icon: transitPinIcon('#DC2626') }).addTo(map).bindPopup('<b>Destination Point</b>');

      // ── 1. Walking Leg (Origin -> Nearest Boarding Stop) ──
      if (nearestMyLoc) {
        activeWalkPolyline1 = L.polyline([myLoc, nearestMyLoc], {
          color: '#475569',
          weight: 4,
          dashArray: '3, 7',
          opacity: 0.9,
          lineCap: 'round',
        }).addTo(map);
      }

      // ── 2. Stored corridor when the two stops share a route, otherwise OSRM ──
      const busStart = nearestMyLoc || myLoc;
      const busEnd = nearestDestLoc || destLoc;
      const shapeEl = document.getElementById('tripShape');
      const etaEl = document.getElementById('tripEta');
      let storedShape = null;
      if (shapeEl && shapeEl.textContent.trim() && shapeEl.textContent.trim() !== 'null') {
        const parsed = JSON.parse(shapeEl.textContent);
        if (Array.isArray(parsed) && parsed.length > 1) storedShape = parsed;
      }
      const etaMin = (etaEl && etaEl.textContent.trim() && etaEl.textContent.trim() !== 'null')
        ? JSON.parse(etaEl.textContent)
        : null;

      let roadPoints = storedShape || [busStart, busEnd];

      if (!storedShape) {
        try {
          const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${busStart[1]},${busStart[0]};${busEnd[1]},${busEnd[0]}?overview=full&geometries=geojson`;
          const res = await fetch(osrmUrl);
          if (res.ok) {
            const json = await res.json();
            if (json.code === 'Ok' && json.routes && json.routes[0]) {
              roadPoints = json.routes[0].geometry.coordinates.map(c => [c[1], c[0]]);
            }
          }
        } catch (osrmErr) {
          console.warn('OSRM routing offline, using direct corridor line:', osrmErr);
        }
      }

      window.planRidePoints = roadPoints;
      activeTransitPolyline = L.polyline(roadPoints, {
        color: '#00B377',
        weight: 6,
        opacity: 1.0,
        lineCap: 'round',
        lineJoin: 'round',
        smoothFactor: 1.2,
      }).addTo(map);

      if (etaMin) {
        const mid = roadPoints[Math.floor(roadPoints.length / 2)];
        L.marker(mid, {
          icon: routeTimeIcon(etaMin),
          interactive: false,
          zIndexOffset: 400,
        }).addTo(map);
      }

      // ── 3. Final Walking Leg (Alighting Stop -> Destination) ──
      if (nearestDestLoc) {
        activeWalkPolyline2 = L.polyline([nearestDestLoc, destLoc], {
          color: '#475569',
          weight: 4,
          dashArray: '3, 7',
          opacity: 0.9,
          lineCap: 'round',
        }).addTo(map);
      }

      // Skip if the user already pressed My Location while this route was loading.
      if ((window.userLocateSeq || 0) === locateAtStart) {
        map.fitBounds([myLoc, destLoc], {
          paddingTopLeft: [400, 60],
          paddingBottomRight: [60, 60],
          maxZoom: 15
        });
      }
    }
  } catch (err) {
    console.error('Error drawing transit route:', err);
  }
});
