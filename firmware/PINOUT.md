# Hardware Wiring & Pin Configuration

This document specifies the electrical wiring and pin connections between the **Arduino Mega 2560** microcontroller, the **u-blox NEO-6M GPS** module, and the **SIM900 GSM/GPRS** module used in the IoT vehicular tracking unit.

---

## 1. Arduino Mega 2560 $\leftrightarrow$ u-blox NEO-6M GPS Module

Serial communication is established via **Hardware Serial 1** at **9600 baud**.

| Arduino Mega 2560 Pin | NEO-6M GPS Pin | Function / Description |
|-----------------------|----------------|------------------------|
| `3.3V`                | `VCC`          | Regulated 3.3V DC power supply |
| `GND`                 | `GND`          | Common ground reference |
| `TX1 (Pin 18)`        | `RX`           | Microcontroller transmit to GPS receive (optional configuration commands) |
| `RX1 (Pin 19)`        | `TX`           | GPS transmits NMEA sentences (GGA, RMC) to microcontroller |

> **Note:** The NEO-6M requires clear line-of-sight to the sky to establish satellite lock (indicated by the onboard blinking LED).

---

## 2. Arduino Mega 2560 $\leftrightarrow$ SIM900 GSM/GPRS Module

Serial communication is established via **Hardware Serial 2** at **9600 baud**.

| Arduino Mega 2560 Pin | SIM900 GSM Pin | Function / Description |
|-----------------------|----------------|------------------------|
| `5V` (or external 2A) | `VCC` / `5V`   | Power input (SIM900 requires up to 2A burst current during transmission) |
| `GND`                 | `GND`          | Common ground reference |
| `TX2 (Pin 16)`        | `RXD`          | Microcontroller transmit to GSM receive (AT commands) |
| `RX2 (Pin 17)`        | `TXD`          | GSM transmits responses (`OK`, HTTP response codes) to microcontroller |

---

## 3. Power Supply Unit

- The IoT unit is powered via a portable battery pack / buck converter supplying:
  - 5V / 2A to the Arduino Mega and SIM900 GSM module.
  - Regulated 3.3V output from Arduino Mega to the NEO-6M GPS module.
