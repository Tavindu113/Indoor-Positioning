#include <WiFi.h>
#include <HTTPClient.h>

// === Wi-Fi to connect for transmitting ===
const char* ssid = "YourWiFiName";            // Transmitting network
const char* password = "YourWiFiPassword";

// === Firebase URL ===
const char* firebaseHost = "https://rssi-input.firebaseio.com";

// === Cart ID (unique per ESP32) ===
const char* cartID = "Cart2";  // Change to Cart2, Cart3, etc. for others

// === Real AP SSIDs and AP Labels ===
const char* ssid_AP1 = "AP_LivingRoom_01";
const char* ssid_AP2 = "AP_Corridor_02";
const char* ssid_AP3 = "AP_Storage_03";

#define AP1_LABEL "AP1"
#define AP2_LABEL "AP2"
#define AP3_LABEL "AP3"

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected.");
}

void loop() {
  Serial.println("Scanning...");

  int n = WiFi.scanNetworks();
  int rssi_AP1 = -999, rssi_AP2 = -999, rssi_AP3 = -999;

  for (int i = 0; i < n; ++i) {
    String foundSSID = WiFi.SSID(i);
    int foundRSSI = WiFi.RSSI(i);

    if (foundSSID == ssid_AP1) rssi_AP1 = foundRSSI;
    else if (foundSSID == ssid_AP2) rssi_AP2 = foundRSSI;
    else if (foundSSID == ssid_AP3) rssi_AP3 = foundRSSI;
  }

  Serial.printf("Scanned RSSI - %s: %d, %s: %d, %s: %d\n",
                AP1_LABEL, rssi_AP1,
                AP2_LABEL, rssi_AP2,
                AP3_LABEL, rssi_AP3);

  // Upload to Firebase
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String path = String("/Location: DMIE Ground/") + cartID + ".json";
    String url = firebaseHost + path;

    String payload = "{";
    payload += "\"" AP1_LABEL "\": " + String(rssi_AP1) + ",";
    payload += "\"" AP2_LABEL "\": " + String(rssi_AP2) + ",";
    payload += "\"" AP3_LABEL "\": " + String(rssi_AP3);
    payload += "}";

    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.PUT(payload);
    Serial.print("Firebase response: ");
    Serial.println(httpResponseCode);

    http.end();
  }

  delay(5000);  // Wait 5 seconds before next scan
}


