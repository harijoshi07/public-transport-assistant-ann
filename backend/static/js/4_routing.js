// ==========================================================================
// Routing Engine — Glowing Metro Corridors & Custom SVG DivIcons
// ==========================================================================

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
      
      // ── Custom SVG DivIcon: Origin Beacon ──
      const originIconHtml = `
        <div class="custom-pin origin-pin">
          <div class="pin-pulse"></div>
          <div class="pin-core"></div>
          <div class="pin-label">Origin Location</div>
        </div>`;
      const originDivIcon = L.divIcon({
        html: originIconHtml,
        className: '',
        iconSize: [36, 48],
        iconAnchor: [18, 11],
        popupAnchor: [0, -16]
      });

      // ── Custom SVG DivIcon: Destination Pin ──
      const destIconHtml = `
        <div class="custom-pin dest-pin">
          <div class="pin-head">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="#E11D48">
              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
            </svg>
          </div>
          <div class="pin-label">Destination</div>
        </div>`;
      const destDivIcon = L.divIcon({
        html: destIconHtml,
        className: '',
        iconSize: [36, 50],
        iconAnchor: [18, 22],
        popupAnchor: [0, -26]
      });

      // ── Custom SVG DivIcon: Transit Stops ──
      const boardingIconHtml = `
        <div class="station-node-pin" style="border-color: #00D2A0; color: #00D2A0;">
          <span>🚌</span>
          <div class="station-node-tooltip">Boarding Stop</div>
        </div>`;
      const boardingDivIcon = L.divIcon({
        html: boardingIconHtml,
        className: '',
        iconSize: [22, 22],
        iconAnchor: [11, 11],
        popupAnchor: [0, -14]
      });

      const alightingIconHtml = `
        <div class="station-node-pin" style="border-color: #2979FF; color: #2979FF;">
          <span>🚏</span>
          <div class="station-node-tooltip">Alighting Stop</div>
        </div>`;
      const alightingDivIcon = L.divIcon({
        html: alightingIconHtml,
        className: '',
        iconSize: [22, 22],
        iconAnchor: [11, 11],
        popupAnchor: [0, -14]
      });

      // Add Markers to Map
      L.marker(myLoc, { icon: originDivIcon }).addTo(map).bindPopup('<b>Origin</b><br>Your Starting Location');
      L.marker(destLoc, { icon: destDivIcon }).addTo(map).bindPopup('<b>Destination</b><br>Final Dropoff Point');

      if (nearestMyLoc && Array.isArray(nearestMyLoc)) {
        L.marker(nearestMyLoc, { icon: boardingDivIcon }).addTo(map).bindPopup('<b>Nearest Boarding Stop</b>');
      }
      if (nearestDestLoc && Array.isArray(nearestDestLoc)) {
        L.marker(nearestDestLoc, { icon: alightingDivIcon }).addTo(map).bindPopup('<b>Nearest Alighting Stop</b>');
      }

      // ── Draw Dual-Layer Glowing Metro Corridors ──
      // 1. Walking Leg (Origin -> Nearest Boarding Stop)
      if (nearestMyLoc) {
        L.polyline([myLoc, nearestMyLoc], {
          color: '#94A3B8',
          weight: 4,
          dashArray: '6, 8',
          opacity: 0.9,
          lineCap: 'round'
        }).addTo(map);
      }

      // 2. Bus Transit Corridor (Boarding Stop -> Alighting Stop)
      const busLegStart = nearestMyLoc || myLoc;
      const busLegEnd = nearestDestLoc || destLoc;

      // Outer Neon Glow Layer
      L.polyline([busLegStart, busLegEnd], {
        color: '#00D2A0',
        weight: 11,
        opacity: 0.35,
        lineCap: 'round',
        lineJoin: 'round'
      }).addTo(map);

      // Core Vibrant Metro Corridor Line
      L.polyline([busLegStart, busLegEnd], {
        color: '#00D2A0',
        weight: 5.5,
        opacity: 1,
        lineCap: 'round',
        lineJoin: 'round'
      }).addTo(map);

      // 3. Final Walking Leg (Alighting Stop -> Destination)
      if (nearestDestLoc) {
        L.polyline([nearestDestLoc, destLoc], {
          color: '#94A3B8',
          weight: 4,
          dashArray: '6, 8',
          opacity: 0.9,
          lineCap: 'round'
        }).addTo(map);
      }

      // Smoothly zoom and center both points with padding
      map.fitBounds([myLoc, destLoc], { padding: [70, 70], maxZoom: 15 });
    }
  } catch (err) {
    console.error('Error drawing transit route:', err);
  }
});
