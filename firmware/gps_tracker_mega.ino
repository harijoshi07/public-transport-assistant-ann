/*
 * Public Transportation Assistance using Artificial Neural Network
 * IoT Vehicle Telemetry Unit
 * 
 * Target Hardware: Arduino Mega 2560
 * Modules: 
 *   - u-blox NEO-6M GPS Module
 *   - SIM900 GSM/GPRS Quad-Band Module
 * 
 * Hardware Serial Mapping (Arduino Mega):
 *   - Serial  (USB): Debug Monitor (9600 baud)
 *   - Serial1 (Pins 19 RX1, 18 TX1): NEO-6M GPS (9600 baud)
 *   - Serial2 (Pins 17 RX2, 16 TX2): SIM900 GSM (9600 baud)
 * 
 * Institution: IOE Thapathali Campus, Tribhuvan University
 * Team: Chandra Mohan Sah, Hari Krishna Joshi, Jyotsna Jha, Khagendra Raj Joshi
 * Supervisor: Er. Kiran Chandra Dahal
 * Date: March 2024
 */

#include <TinyGPS++.h>

// Create TinyGPS++ parser instance
TinyGPSPlus gps;

// Configuration Constants
const unsigned long UPDATE_INTERVAL = 30000; // Transmit every 30 seconds
const char* APN = "web";                     // Mobile network APN (e.g., Ncell/NTC)
const char* THINGSPEAK_API_KEY = "YOUR_THINGSPEAK_WRITE_API_KEY";
const int DEVICE_ID = 1;                     // Unique bus identifier

unsigned long lastTransmitTime = 0;

void setup() {
  // Initialize USB Serial for debugging
  Serial.begin(9600);
  while (!Serial) { ; }
  Serial.println(F("[SYSTEM] Public Transport Assistant Telemetry Starting..."));

  // Initialize Hardware Serial 1 for GPS (NEO-6M)
  Serial1.begin(9600);
  Serial.println(F("[GPS] Initialized Serial1 at 9600 baud."));

  // Initialize Hardware Serial 2 for GSM (SIM900)
  Serial2.begin(9600);
  Serial.println(F("[GSM] Initialized Serial2 at 9600 baud."));

  delay(3000); // Allow SIM900 time to register to the cellular network
  initGPRS();
}

void loop() {
  // Feed incoming GPS NMEA sentences into the TinyGPS++ parser
  while (Serial1.available() > 0) {
    gps.encode(Serial1.read());
  }

  // Check if it is time to transmit telemetry (every 30 seconds)
  if (millis() - lastTransmitTime >= UPDATE_INTERVAL) {
    if (gps.location.isValid()) {
      float latitude = gps.location.lat();
      float longitude = gps.location.lng();
      float speedKmh = gps.speed.kmph();

      Serial.print(F("[TELEMETRY] Valid GPS Fix: Lat="));
      Serial.print(latitude, 6);
      Serial.print(F(", Lng="));
      Serial.print(longitude, 6);
      Serial.print(F(", Speed="));
      Serial.print(speedKmh, 2);
      Serial.println(F(" km/h"));

      sendLocationToThingSpeak(latitude, longitude, speedKmh, DEVICE_ID);
    } else {
      Serial.println(F("[GPS] Waiting for valid satellite lock..."));
    }
    lastTransmitTime = millis();
  }
}

// Send AT command and wait for expected response
bool sendATCommand(const String& command, const char* expectedResponse, unsigned long timeoutMs) {
  Serial2.println(command);
  Serial.print(F(" -> AT: "));
  Serial.println(command);

  unsigned long start = millis();
  String response = "";

  while (millis() - start < timeoutMs) {
    while (Serial2.available() > 0) {
      char c = Serial2.read();
      response += c;
    }
    if (response.indexOf(expectedResponse) != -1) {
      Serial.println(F("    Response: OK"));
      return true;
    }
  }

  Serial.print(F("    Response TIMEOUT: "));
  Serial.println(response);
  return false;
}

// Initialize SIM900 GPRS Bearer Profile
void initGPRS() {
  Serial.println(F("[GSM] Initializing GPRS profile..."));
  sendATCommand("AT", "OK", 2000);
  sendATCommand("AT+CIPSHUT", "SHUT OK", 3000);
  sendATCommand("AT+SAPBR=3,1,\"Contype\",\"GPRS\"", "OK", 3000);
  
  String apnCmd = "AT+SAPBR=3,1,\"APN\",\"" + String(APN) + "\"";
  sendATCommand(apnCmd, "OK", 3000);
  sendATCommand("AT+SAPBR=1,1", "OK", 10000); // Activate bearer
  sendATCommand("AT+SAPBR=2,1", "OK", 5000);  // Query assigned IP
}

// Transmit coordinates to ThingSpeak IoT Analytics Server
void sendLocationToThingSpeak(float lat, float lng, float speed, int busId) {
  Serial.println(F("[HTTP] Building ThingSpeak telemetry request..."));

  // Build HTTP GET/POST URL
  // Field 1: Device ID, Field 2: Latitude, Field 3: Longitude, Field 4: Speed
  String url = "http://api.thingspeak.com/update?api_key=" + String(THINGSPEAK_API_KEY) +
               "&field1=" + String(busId) +
               "&field2=" + String(lat, 6) +
               "&field3=" + String(lng, 6) +
               "&field4=" + String(speed, 2);

  sendATCommand("AT+HTTPINIT", "OK", 3000);
  sendATCommand("AT+HTTPPARA=\"CID\",1", "OK", 3000);
  
  String urlCmd = "AT+HTTPPARA=\"URL\",\"" + url + "\"";
  sendATCommand(urlCmd, "OK", 5000);
  
  // Submit HTTP GET action
  sendATCommand("AT+HTTPACTION=0", "OK", 10000);
  delay(2000);
  sendATCommand("AT+HTTPREAD", "OK", 5000);
  sendATCommand("AT+HTTPTERM", "OK", 3000);

  Serial.println(F("[HTTP] Telemetry transmission complete."));
}
