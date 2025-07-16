#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <esp_system.h>

const char* ssid = "Marlon_S world";
const char* password = "Maryas@2@";
const char* firebaseHost = "https://rssi-input-default-rtdb.asia-southeast1.firebasedatabase.app";
const char* cartID = "Cart1";

const char* ssid_AP1 = "DMIE_Lab_AP1";
const char* ssid_AP2 = "DMIE_Lab_AP2";
const char* ssid_AP3 = "DMIE_Lab_AP3";
const char* ssid_AP4 = "DMIE_Lab_AP4";

#define AP1_LABEL "AP1"
#define AP2_LABEL "AP2"
#define AP3_LABEL "AP3"
#define AP4_LABEL "AP4"

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }
  Serial.println("Program started!");
  Serial.print("Reset reason: ");
  Serial.println(esp_reset_reason());
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
  Serial.println("\nStarting loop...");
  Serial.println("Scanning nearby networks...");

  int n = WiFi.scanNetworks();
  Serial.print("Number of networks found: ");
  Serial.println(n);

  int rssi_AP1 = -999, rssi_AP2 = -999, rssi_AP3 = -999, rssi_AP4 = -999;

  for (int i = 0; i < n; ++i) {
    String foundSSID = WiFi.SSID(i);
    int foundRSSI = WiFi.RSSI(i);
    Serial.println("Found SSID: " + foundSSID + ", RSSI: " + foundRSSI);
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

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure();

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
    if (responseCode > 0) {
      Serial.println("HTTP request successful");
    } else {
      Serial.println("HTTP request failed");
    }

    String response = http.getString();
    Serial.println("Firebase response body: " + response);

    http.end();
  } else {
    Serial.println("WiFi not connected - skipping upload.");
  }

  delay(1000);
}