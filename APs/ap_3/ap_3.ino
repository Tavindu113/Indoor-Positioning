#include <WiFi.h>
#include <esp_wifi.h>

const char* ssid = "DMIE_Lab_AP3";
const char* password = "DMIE_Lab_AP3"; // Replace with any password (min 8 characters)

void setup() {
  Serial.begin(115200);
  WiFi.setTxPower(WIFI_POWER_21dBm);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  Serial.println("Access Point started");
  Serial.print("SSID: ");
  Serial.println(ssid);
}

void loop() {}