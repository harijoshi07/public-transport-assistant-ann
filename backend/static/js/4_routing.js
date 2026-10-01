// ==========================================================================
// Street-Accurate Routing Engine (OSRM) with Dual-Layer Framed Polylines
// ==========================================================================

let activeCasingPolyline = null;
let activeCorePolyline = null;
let activeWalkPolyline1 = null;
let activeWalkPolyline2 = null;

// Function to dynamically update polyline colors based on active theme
window.applyPolylineTheme = function (isDark) {
  if (activeCasingPolyline) {
    activeCasingPolyline.setStyle({
      color: isDark ? '#0A0E17' : '#FFFFFF',
      opacity: isDark ? 0.9 : 0.95,
    });
  }
  if (activeCorePolyline) {
    activeCorePolyline.setStyle({
      color: isDark ? '#00D2A0' : '#1D4ED8', // Vibrant neon teal in dark, royal sapphire in light
    });
  }
  if (activeWalkPolyline1) {
    activeWalkPolyline1.setStyle({
      color: isDark ? '#94A3B8' : '#475569',
    });
  }
  if (activeWalkPolyline2) {
    activeWalkPolyline2.setStyle({
      color: isDark ? '#94A3B8' : '#475569',
    });
  }
};

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
      const isDark = (localStorage.getItem('transit_app_theme') || 'dark') === 'dark';

      // ── Custom SVG DivIcon: Origin Beacon ──
      const originDivIcon = L.divIcon({
        html: `
          <div class="custom-pin origin-pin">
            <div class="pin-pulse"></div>
            <div class="pin-core"></div>
            <div class="pin-label">Origin</div>
          </div>`,
        className: '',
        iconSize: [36, 48],
        iconAnchor: [18, 11],
        popupAnchor: [0, -16]
      });

      // ── Custom SVG DivIcon: Destination Pin ──
      const destDivIcon = L.divIcon({
        html: `
          <div class="custom-pin dest-pin">
            <div class="pin-head">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="#E11D48">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
              </svg>
            </div>
            <div class="pin-label">Destination</div>
          </div>`,
        className: '',
        iconSize: [36, 50],
        iconAnchor: [18, 24],
        popupAnchor: [0, -28]
      });

      // ── Custom SVG DivIcon: Transit Stops ──
      const boardingDivIcon = L.divIcon({
        html: `
          <div class="station-node-pin" style="border-color: #00D2A0; color: #00D2A0;">
            <span style="font-size: 11px;">🚌</span>
            <div class="station-node-tooltip">Nearest Boarding Stop</div>
          </div>`,
        className: '',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -14]
      });

      const alightingDivIcon = L.divIcon({
        html: `
          <div class="station-node-pin" style="border-color: #2563EB; color: #2563EB;">
            <span style="font-size: 11px;">🚏</span>
            <div class="station-node-tooltip">Nearest Alighting Stop</div>
          </div>`,
        className: '',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -14]
      });

      // Add Markers
      L.marker(myLoc, { icon: originDivIcon }).addTo(map).bindPopup('<b>Starting Location</b>');
      L.marker(destLoc, { icon: destDivIcon }).addTo(map).bindPopup('<b>Destination Point</b>');

      if (nearestMyLoc && Array.isArray(nearestMyLoc)) {
        L.marker(nearestMyLoc, { icon: boardingDivIcon }).addTo(map).bindPopup('<b>Boarding Transit Stop</b>');
      }
      if (nearestDestLoc && Array.isArray(nearestDestLoc)) {
        L.marker(nearestDestLoc, { icon: alightingDivIcon }).addTo(map).bindPopup('<b>Alighting Transit Stop</b>');
      }

      // ── 1. Walking Leg (Origin -> Nearest Boarding Stop) ──
      if (nearestMyLoc) {
        activeWalkPolyline1 = L.polyline([myLoc, nearestMyLoc], {
          color: isDark ? '#94A3B8' : '#475569',
          weight: 3.5,
          dashArray: '4, 8',
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

      // Layer 1: Contrast Casing Ribbon (separates polyline from map roads)
      activeCasingPolyline = L.polyline(roadPoints, {
        color: isDark ? '#0A0E17' : '#FFFFFF',
        weight: 8,
        opacity: isDark ? 0.9 : 0.95,
        lineCap: 'round',
        lineJoin: 'round',
      }).addTo(map);

      // Layer 2: Core Metro Corridor Line (Vibrant in both themes)
      activeCorePolyline = L.polyline(roadPoints, {
        color: isDark ? '#00D2A0' : '#1D4ED8',
        weight: 5,
        opacity: 1.0,
        lineCap: 'round',
        lineJoin: 'round',
      }).addTo(map);

      // ── 3. Final Walking Leg (Alighting Stop -> Destination) ──
      if (nearestDestLoc) {
        activeWalkPolyline2 = L.polyline([nearestDestLoc, destLoc], {
          color: isDark ? '#94A3B8' : '#475569',
          weight: 3.5,
          dashArray: '4, 8',
          opacity: 0.9,
          lineCap: 'round',
        }).addTo(map);
      }

      // Fit map bounds smoothly
      map.fitBounds([myLoc, destLoc], { padding: [70, 70], maxZoom: 15 });
    }
  } catch (err) {
    console.error('Error drawing transit route:', err);
  }
});
