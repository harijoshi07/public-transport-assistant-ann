// Blue location puck. One geolocation request at a time so a click is not
// dropped while another lookup is still running.
let userMarker = null;
let userAccuracy = null;
let lastFix = null;
let fixInFlight = false;
let recenterAfterFix = false;
let trackingStarted = false;

window.userLocateSeq = 0;
window.geoPermissionState = 'unknown';

function userLocationIcon() {
  const html = `
    <div class="user-loc">
      <span class="user-loc-ring"></span>
      <span class="user-loc-dot"></span>
    </div>`;
  return L.divIcon({
    html: html,
    className: '',
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });
}

function updateMarkerLocation(lat, lng, accuracy) {
  const point = [lat, lng];
  if (!userMarker) {
    userMarker = L.marker(point, {
      icon: userLocationIcon(),
      zIndexOffset: 800,
      interactive: false,
    }).addTo(map);
  } else {
    userMarker.setLatLng(point);
  }

  const meters = Number(accuracy);
  if (meters > 8 && meters < 800) {
    if (!userAccuracy) {
      userAccuracy = L.circle(point, {
        radius: meters,
        color: '#4285F4',
        weight: 1,
        opacity: 0.35,
        fillColor: '#4285F4',
        fillOpacity: 0.12,
        interactive: false,
      }).addTo(map);
    } else {
      userAccuracy.setLatLng(point);
      userAccuracy.setRadius(meters);
    }
  } else if (userAccuracy) {
    map.removeLayer(userAccuracy);
    userAccuracy = null;
  }
}

function setLocating(active) {
  const btn = document.getElementById('btnMyLocation');
  if (btn) btn.classList.toggle('is-locating', !!active);
}

function markLocationBlocked() {
  recenterAfterFix = false;
  setLocating(false);
  const btn = document.getElementById('btnMyLocation');
  if (btn) btn.title = 'Location is blocked in the browser';
}

function flyToFix(lat, lng) {
  if (typeof map === 'undefined' || !map) return;
  setLocating(false);
  if (typeof map.stop === 'function') map.stop();
  map.invalidateSize({ pan: false, animate: false });
  map.flyTo([lat, lng], 16, { duration: 1.5 });
}

function rememberFix(position) {
  lastFix = {
    lat: position.coords.latitude,
    lng: position.coords.longitude,
    accuracy: position.coords.accuracy,
  };
  updateMarkerLocation(lastFix.lat, lastFix.lng, lastFix.accuracy);
}

function geoTimeoutMs() {
  // A short timeout expires while the permission prompt is still open.
  return window.geoPermissionState === 'granted' ? 8000 : 60000;
}

function requestFix(highAccuracy) {
  if (fixInFlight || !navigator.geolocation) return;
  if (window.geoPermissionState === 'denied') {
    markLocationBlocked();
    return;
  }

  fixInFlight = true;
  navigator.geolocation.getCurrentPosition(
    function (position) {
      fixInFlight = false;
      const previous = lastFix;
      rememberFix(position);
      if (recenterAfterFix) {
        recenterAfterFix = false;
        const shifted = !previous || map.distance(
          [previous.lat, previous.lng],
          [lastFix.lat, lastFix.lng]
        ) > 40;
        if (shifted) flyToFix(lastFix.lat, lastFix.lng);
        else setLocating(false);
      }
    },
    function (error) {
      fixInFlight = false;
      if (error && error.code === 1) {
        markLocationBlocked();
        return;
      }
      if (highAccuracy) {
        requestFix(false);
        return;
      }
      if (recenterAfterFix && lastFix) {
        recenterAfterFix = false;
        flyToFix(lastFix.lat, lastFix.lng);
        return;
      }
      recenterAfterFix = false;
      setLocating(false);
    },
    {
      enableHighAccuracy: !!highAccuracy,
      timeout: highAccuracy ? geoTimeoutMs() : 10000,
      maximumAge: highAccuracy ? 10000 : 60000,
    }
  );
}

function startTracking() {
  if (trackingStarted) return;
  trackingStarted = true;
  setInterval(function () {
    if (!fixInFlight && !recenterAfterFix) requestFix(false);
  }, 15000);
}

function getUserLocation(recenter) {
  if (!navigator.geolocation || typeof map === 'undefined') return;
  if (window.geoPermissionState === 'denied') {
    markLocationBlocked();
    return;
  }

  if (recenter) {
    window.userLocateSeq = (window.userLocateSeq || 0) + 1;
    recenterAfterFix = true;
    if (lastFix) {
      flyToFix(lastFix.lat, lastFix.lng);
    } else {
      setLocating(true);
    }
  }

  requestFix(true);
  startTracking();
}

document.addEventListener('DOMContentLoaded', function () {
  if (!navigator.geolocation || !navigator.permissions || !navigator.permissions.query) return;
  navigator.permissions.query({ name: 'geolocation' }).then(function (status) {
    window.geoPermissionState = status.state;
    status.onchange = function () {
      window.geoPermissionState = status.state;
    };
    if (status.state === 'granted') {
      requestFix(true);
      startTracking();
    }
  }).catch(function () {});
});
