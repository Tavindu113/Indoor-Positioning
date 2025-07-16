#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

// === Wi-Fi network used for Internet (NOT the APs being scanned) ===
const char* ssid = "Marlon_S world";       // Replace with your Wi-Fi name
const char* password = "Maryas@2@";        // Replace with your Wi-Fi password

// === Firebase Realtime DB base URL (NO trailing slash, must be HTTPS) ===
const char* firebaseHost = "https://rssi-input-default-rtdb.asia-southeast1.firebasedatabase.app";

// === This cart's unique ID ===
const char* cartID = "Cart1";  // Change for each device if needed

// === Actual SSID names of the 4 APs (broadcasted by XIAO ESP32-S3) ===
const char* ssid_AP1 = "DMIE_Lab_AP1";
const char* ssid_AP2 = "DMIE_Lab_AP2";
const char* ssid_AP3 = "DMIE_Lab_AP3";
const char* ssid_AP4 = "DMIE_Lab_AP4";

// === AP label keys expected by the trilateration server ===
#define AP1_LABEL "AP1"
#define AP2_LABEL "AP2"
#define AP3_LABEL "AP3"
#define AP4_LABEL "AP4"

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  Serial.println("\nScanning nearby networks...");

  int n = WiFi.scanNetworks();
  int rssi_AP1 = -999, rssi_AP2 = -999, rssi_AP3 = -999, rssi_AP4 = -999;

  for (int i = 0; i < n; ++i) {
    String foundSSID = WiFi.SSID(i);
    int foundRSSI = WiFi.RSSI(i);

    if (foundSSID == ssid_AP1) rssi_AP1 = foundRSSI;
    else if (foundSSID == ssid_AP2) rssi_AP2 = foundRSSI;
    else if (foundSSID == ssid_AP3) rssi_AP3 = foundRSSI;
    else if (foundSSID == ssid_AP4) rssi_AP4 = foundRSSI;
  }

  Serial.printf("Scanned RSSI - %s: %d, %s: %d, %s: %d, %s: %d\n",
                AP1_LABEL, rssi_AP1,
                AP2_LABEL, rssi_AP2,
                AP3_LABEL, rssi_AP3,
                AP4_LABEL, rssi_AP4);

  // === Upload RSSI values to Firebase ===
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure();  // Skip cert verification for testing only

    HTTPClient http;

    String path = String("/Location_DMIE_Ground/") + cartID + ".json";
    String url = firebaseHost + path;

    String payload = "{";
    payload += "\"" AP1_LABEL "\": " + String(rssi_AP1) + ",";
    payload += "\"" AP2_LABEL "\": " + String(rssi_AP2) + ",";
    payload += "\"" AP3_LABEL "\": " + String(rssi_AP3) + ",";
    payload += "\"" AP4_LABEL "\": " + String(rssi_AP4);
    payload += "}";

    Serial.print("Uploading to Firebase: ");
    Serial.println(url);
    Serial.print("Payload: ");
    Serial.println(payload);

    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");

    int responseCode = http.PUT(payload);
    Serial.print("Firebase response code: ");
    Serial.println(responseCode);

    String response = http.getString();
    Serial.println("Firebase response body: " + response);

    http.end();
  }

  delay(1000);  // Scan + upload every second
}

