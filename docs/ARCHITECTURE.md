# System Architecture & Technical Specification

The **Public Transportation Assistance System** is an end-to-end cyber-physical architecture designed to eliminate uncertainty in public bus transit within the Kathmandu Valley. It bridges embedded telemetry hardware, cloud message queuing, asynchronous web sockets, machine learning ETA prediction, and client-side map rendering.

---

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EMBEDDED IoT HARDWARE                    │
│                                                             │
│   ┌────────────────┐           ┌────────────────────────┐   │
│   │ u-blox NEO-6M  │──[UART1]─►│   Arduino Mega 2560    │   │
│   │   GPS Module   │ 9600 baud │  (NMEA TinyGPS Parser) │   │
│   └────────────────┘           └───────────┬────────────┘   │
│                                            │ [UART2]        │
│                                            ▼                │
│                                ┌────────────────────────┐   │
│                                │    SIM900 GSM/GPRS     │   │
│                                │ (AT Commands / 9600 b) │   │
│                                └───────────┬────────────┘   │
└────────────────────────────────────────────┼────────────────┘
                                             │ HTTP POST (GPRS / 30s)
                                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   CLOUD TELEMETRY INGESTION                 │
│                                                             │
│                 ThingSpeak IoT Cloud Analytics              │
│                Channels API (Field 1..4 Storage)            │
└────────────────────────────────────────────┬────────────────┘
                                             │ Poll (Every 5s)
                                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  DJANGO BACKEND APPLICATION                 │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │   Hardware_APP: GPS Ingestion Endpoint              │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │   RoutePlot_APP: Routing, Geocoding, & Fares        │   │
│   │   • Nominatim Geocoding API                         │   │
│   │   • Graphhopper Road Network Topology               │   │
│   │   • Distance-based fare calculation                 │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │   ETA_APP / ML Module                               │   │
│   │   • 3-Layer Dense Feedforward Neural Network        │   │
│   │   • Evaluates real-time traffic delay & arrival ETA │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │   API_CONSUMER: Django Channels (WebSockets)        │   │
│   │   • Asynchronous WebSocket event broadcaster        │   │
│   └──────────────────────────┬──────────────────────────┘   │
└──────────────────────────────┼──────────────────────────────┘
                               │ WebSocket (Bidirectional, Live Push)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTERACTIVE WEB INTERFACE                 │
│                                                             │
│   Leaflet.js + OpenStreetMap (OSM) / MapTiler Tiles         │
│   • Live moving vehicle markers                             │
│   • Sequential bus corridor overlays                        │
│   • Nearest bus station discovery (Geodesic distance)       │
│   • Dynamic ETA countdown and transit fare display          │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Embedded Hardware (IoT Unit)
- **Controller:** Arduino Mega 2560 (8-bit ATmega2560 @ 16 MHz, 8 KB SRAM, 256 KB Flash).
- **Positioning:** u-blox NEO-6M GPS receiver providing 50-channel tracking, 2.5m horizontal accuracy, and 1 Hz NMEA output.
- **Cellular Transmission:** SIM900 Quad-Band GSM/GPRS module operating on standard AT commands over TCP/IP GPRS stack.
- **Sampling Frequency:** Transmits coordinates every 30 seconds to conserve bandwidth while providing sufficient spatial tracking accuracy.

### 2.2 Cloud & Ingestion Layer
- **ThingSpeak API:** Intermediary buffer separating the mobile cellular link from server infrastructure.
- **Fields:**
  - Field 1: Device ID / Vehicle Identifier
  - Field 2: Latitude
  - Field 3: Longitude
  - Field 4: Speed (km/h)

### 2.3 Backend & Asynchronous WebSockets
- **Framework:** Django 4.0 + Django REST Framework.
- **Asynchronous Protocol:** Django Channels with WebSockets (ASGI). A background worker continuously polls ThingSpeak updates every 5 seconds and pushes the new coordinate stream down the active WebSocket pipe to all connected browser clients.

### 2.4 Machine Learning ETA Model
- **Algorithm:** Artificial Neural Network (ANN) regression.
- **Topology:** Input (10) $\rightarrow$ Dense (64, ReLU) $\rightarrow$ Dropout (0.3) $\rightarrow$ Dense (32, ReLU) $\rightarrow$ Dropout (0.3) $\rightarrow$ Dense (1, Linear).
- **Performance:** Achieved an $R^2$ score of **0.965** and a Mean Absolute Percentage Error (MAPE) of **6.74%** on held-out test data.

### 2.5 Geospatial & Routing Services
- **Geocoding:** Nominatim geocoding via `geopy` resolves arbitrary Kathmandu place names into coordinate pairs.
- **Nearest Stop Search:** Scans Kathmandu station database and computes minimum geodesic distance using the WGS-84 ellipsoidal model.
- **Fare Computation:** Follows Kathmandu local government transit tariffs (Rs. 20 base for $<5$ km, +Rs. 5 for every additional 5 km interval).
