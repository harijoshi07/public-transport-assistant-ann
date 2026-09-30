# Public Transportation Assistance using Artificial Neural Network

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.0-092E20.svg)](https://www.djangoproject.com/)
[![Arduino](https://img.shields.io/badge/Arduino-Mega%202560-00979D.svg)](https://www.arduino.cc/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-Keras-FF6F00.svg)](https://www.tensorflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Institution](https://img.shields.io/badge/IOE-Thapathali%20Campus-red.svg)](https://tcioe.edu.np/)

An end-to-end cyber-physical public transit tracking and arrival prediction system developed at **Tribhuvan University, Institute of Engineering (IOE), Thapathali Campus**. 

The system couples **embedded IoT hardware** (Arduino Mega, u-blox NEO-6M GPS, SIM900 GSM) with a **Django REST & WebSockets backend**, a **Deep Feedforward Neural Network (ANN)** for Estimated Time of Arrival (ETA) prediction ($R^2 = 0.965$), and an **interactive Leaflet/OpenStreetMap interface** to eliminate transit scheduling uncertainty across public bus corridors in the Kathmandu Valley.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EMBEDDED IoT HARDWARE                    │
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
│                 CLOUD TELEMETRY INGESTION                   │
│          ThingSpeak IoT Cloud Analytics Channels API        │
└────────────────────────────────────────────┬────────────────┘
                                             │ Polling (Every 5s)
                                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  DJANGO BACKEND APPLICATION                 │
│   • Hardware_APP  : Ingestion endpoint from telemetry       │
│   • RoutePlot_APP : Graphhopper routing & geodesic geocoding│
│   • ETA_APP / ML  : Feedforward Dense ANN for arrival times │
│   • API_CONSUMER  : Django Channels (WebSockets broadcaster)│
└──────────────────────────────┬──────────────────────────────┘
                               │ WebSocket (Bidirectional, Live Push)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  INTERACTIVE WEB INTERFACE                  │
│       Leaflet.js + OpenStreetMap (OSM) / MapTiler Tiles     │
│   • Real-time moving bus markers with route polyline traces │
│   • Nearest stop discovery via geodesic distance            │
│   • Distance-based dynamic fare computation (Tariff rules)  │
│   • Neural network arrival countdown display                │
└─────────────────────────────────────────────────────────────┘
```

---

## Repository Structure (Monorepo)

```
public-transport-assistant-ann/
├── firmware/                   # Arduino microcontroller firmware & pinouts
│   ├── gps_tracker_mega.ino    # Arduino Mega C++ sketch (TinyGPS++ & SIM900 GPRS)
│   └── PINOUT.md               # Hardware wiring & pin configuration tables
├── backend/                    # Django 4.0 REST Framework & WebSockets server
│   ├── manage.py               # Django management CLI
│   ├── PROJECT_MAP_API/        # Project settings, ASGI/WSGI, routing configs
│   ├── RoutePlot_APP/          # Routes, stations, fare algorithms, management seeders
│   ├── Hardware_APP/           # Direct GPS ingestion API endpoints
│   ├── API_CONSUMER/           # Asynchronous Channels WebSockets consumers
│   ├── Data/                   # Seed CSV datasets for Kathmandu transit network
│   ├── templates/              # Jinja2 / HTML templates for Leaflet map interface
│   ├── static/                 # Stylesheets, JavaScript, and custom map icons
│   └── geoJson_converter/      # GeoJSON converters for spatial corridor networks
├── ml/                         # Machine learning model & ETA pipeline
│   ├── train_eta_ann.py        # Keras/TensorFlow ANN training pipeline (64-32-1)
│   └── README.md               # Model specifications, hyperparameters, error metrics
├── data/                       # Structured Kathmandu public transit datasets
│   ├── stationinfo.csv         # 100+ bus stations with coordinate geocodes
│   ├── routeinfo.csv           # Public transit corridors (origin, terminal, IDs)
│   ├── routestationinfo.csv    # Ordered sequential stop connections per route
│   └── README.md               # Dataset documentation & relational schema
├── docs/                       # Architectural documentation & technical specs
│   └── ARCHITECTURE.md         # Full system architecture specification
├── .env.example                # Example environment variables
├── .gitignore                  # Production Python/Django/OS ignore rules
├── requirements.txt            # Python dependencies
└── README.md                   # Repository overview
```

---

## Machine Learning: ETA Prediction Model

As documented in **Section 5.2.3** of the Project Report, a feedforward dense neural network was trained on historical bus GPS records across Kathmandu transit corridors.

### Architecture
- **Input Layer:** 10 normalized features (`current_station`, `next_station`, `hour_of_day`, `distance_km`, `speed_kmh`, `congestion_index`, `day_of_week`, `elevation_delta`, `weather_factor`, `stops_remaining`)
- **Hidden Layer 1:** Dense(64, ReLU) + Dropout(0.3)
- **Hidden Layer 2:** Dense(32, ReLU) + Dropout(0.3)
- **Output Layer:** Dense(1, Linear) $\rightarrow$ Predicted Travel Time
- **Optimizer:** Adam | **Loss Function:** Mean Absolute Error (MAE)

### Empirical Evaluation (Held-Out 20% Test Set)

| Metric | Measured Value | Analysis |
|--------|----------------|----------|
| **Coefficient of Determination ($R^2$)** | **0.965** | Captures 96.5% of variance in transit travel times |
| **Mean Absolute Percentage Error (MAPE)** | **6.74%** | Average prediction deviation from actual arrival |
| **Mean Absolute Error (MAE)** | **0.00067** | Normalized deviation on held-out test data |
| **Root Mean Squared Error (RMSE)** | **0.00194** | Low error variance across spatial segments |
| **Mean Squared Error (MSE)** | **$3.75 \times 10^{-6}$** | Rapid loss convergence during training |

---

## Hardware Specifications & Wiring

| Arduino Mega 2560 Pin | Connected Module | Function |
|-----------------------|------------------|----------|
| `3.3V` & `GND` | u-blox NEO-6M GPS | Regulated DC power |
| `RX1 (Pin 19)` | NEO-6M `TX` | NMEA sentence serial input (9600 baud) |
| `TX1 (Pin 18)` | NEO-6M `RX` | Configuration commands |
| `5V` & `GND` | SIM900 GSM/GPRS | Power supply (up to 2A peak current) |
| `RX2 (Pin 17)` | SIM900 `TXD` | Cellular AT command responses (9600 baud) |
| `TX2 (Pin 16)` | SIM900 `RXD` | AT commands transmission for GPRS HTTP POST |

*See [`firmware/PINOUT.md`](firmware/PINOUT.md) for full schematics and details.*

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Arduino IDE (if flashing embedded hardware)
- Git

### 2. Installation & Setup

```bash
# Clone the repository
git clone https://github.com/harijoshi07/public-transport-assistant-ann.git
cd public-transport-assistant-ann

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Initialization & Data Seeding

```bash
cd backend

# Copy environment template
cp ../.env.example .env

# Apply database migrations
python manage.py migrate

# Seed transit stations (100+ Kathmandu stops)
python manage.py insert_stationsinfo

# Seed transit corridors
python manage.py insert_routeinfo

# Seed ordered station-to-route connections
python manage.py insert_routeStaioninfo
```

### 4. Running the Development Server

```bash
# Start Django server
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/` to access the live Leaflet map interface.

---

## Academic Attribution & Team

This project was developed and defended as an academic minor project at **Tribhuvan University, Institute of Engineering (IOE), Thapathali Campus** (Department of Electronics and Computer Engineering), March 2024.

- **Project Supervisor:** Er. Kiran Chandra Dahal (Department of Electronics and Computer Engineering, IOE Thapathali Campus)
- **External Examiner:** Er. Yogesh Aryal (Ministry of Education, Science and Technology, Singhadurbar, Kathmandu)

### Team Members:
- **Chandra Mohan Sah** (THA077BEI017)
- **Hari Krishna Joshi** (THA077BEI018) — *Team Lead*
- **Jyotsna Jha** (THA077BEI019)
- **Khagendra Raj Joshi** (THA077BEI022)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
