# Kathmandu Public Transit Dataset

This directory contains the structured geospatial and routing datasets for public bus corridors in the Kathmandu Valley, compiled during the minor project at **IOE Thapathali Campus**.

---

## Files Overview

| File | Records / Size | Description |
|------|----------------|-------------|
| `stationinfo.csv` | ~624 KB | Geographic coordinates, station IDs, English and Nepali names of 100+ public transit stops in Kathmandu |
| `routeinfo.csv` | ~37 KB | Bus corridor IDs, route English/Nepali names, origin (start), and terminal (end) points |
| `routestationinfo.csv` | ~285 KB | Ordered relational table linking routes to their sequential bus stops |
| `device1RouteStation.csv` | ~1 KB | Real-world validation corridor used during prototype testing |
| `average_travel_time_negative_dir.csv` | ~263 B | Empirical travel time baselines across key transit segments |
| `gpsdata.json` | ~583 B | Sample telemetry payload format received from the IoT tracker |

---

## Database Seeding into Django

To populate your local SQLite / PostgreSQL database using these CSV datasets:

```bash
cd backend

# Apply base database migrations
python manage.py migrate

# Seed transit stations
python manage.py insert_stationsinfo

# Seed routes
python manage.py insert_routeinfo

# Seed ordered route-to-station relationships
python manage.py insert_routeStaioninfo
```
