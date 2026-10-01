// ==========================================================================
// Street-Accurate Routing Engine (OSRM) — Matches Transit App Screenshot
// ==========================================================================

let activeTransitPolyline = null;
let activeWalkPolyline1 = null;
let activeWalkPolyline2 = null;

document.addEventListener('DOMContentLoaded', async function () {
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
      
      // ── Red Origin Teardrop Pin (Matching Screenshot) ──
      const originIconHtml = `
        <div style="filter: drop-shadow(0 4px 10px rgba(0,0,0,0.35)); cursor: pointer;">
          <svg width="32" height="42" viewBox="0 0 24 32" fill="none">
            <path d="M12 0C5.37 0 0 5.37 0 12C0 22 12 32 12 32C12 32 24 22 24 12C24 5.37 18.63 0 12 0Z" fill="#DC2626"/>
            <circle cx="12" cy="11" r="5" fill="#FFFFFF"/>
            <circle cx="12" cy="11" r="2.5" fill="#DC2626"/>
          </svg>
        </div>`;

      const originDivIcon = L.divIcon({
        html: originIconHtml,
        className: '',
        iconSize: [32, 42],
        iconAnchor: [16, 40],
        popupAnchor: [0, -36]
      });

      // ── Green Destination Teardrop Pin (Matching Screenshot) ──
      const destIconHtml = `
        <div style="filter: drop-shadow(0 4px 10px rgba(0,0,0,0.35)); cursor: pointer;">
          <svg width="32" height="42" viewBox="0 0 24 32" fill="none">
            <path d="M12 0C5.37 0 0 5.37 0 12C0 22 12 32 12 32C12 32 24 22 24 12C24 5.37 18.63 0 12 0Z" fill="#00B377"/>
            <circle cx="12" cy="11" r="5" fill="#FFFFFF"/>
            <circle cx="12" cy="11" r="2.5" fill="#00B377"/>
          </svg>
        </div>`;

      const destDivIcon = L.divIcon({
        html: destIconHtml,
        className: '',
        iconSize: [32, 42],
        iconAnchor: [16, 40],
        popupAnchor: [0, -36]
      });

      // Add Markers
      L.marker(myLoc, { icon: originDivIcon }).addTo(map).bindPopup('<b>Starting Location</b>');
      L.marker(destLoc, { icon: destDivIcon }).addTo(map).bindPopup('<b>Destination Point</b>');

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

      // ── 2. Street-Accurate Transit Corridor (OSRM Road Network) ──
      const busStart = nearestMyLoc || myLoc;
      const busEnd = nearestDestLoc || destLoc;

      let roadPoints = [busStart, busEnd];

      // Query OSRM routing engine for real Kathmandu street curves
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

      // Transit App Signature Vibrant Green Road Line (weight 6px)
      activeTransitPolyline = L.polyline(roadPoints, {
        color: '#00B377',
        weight: 6,
        opacity: 1.0,
        lineCap: 'round',
        lineJoin: 'round',
      }).addTo(map);

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

      // Fit map bounds smoothly with padding for the left sidebar
      map.fitBounds([myLoc, destLoc], {
        paddingTopLeft: [400, 60],
        paddingBottomRight: [60, 60],
        maxZoom: 15
      });
    }
  } catch (err) {
    console.error('Error drawing transit route:', err);
  }
});
