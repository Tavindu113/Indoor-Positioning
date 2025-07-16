#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  
  // Set device as a WiFi Station
  WiFi.mode(WIFI_STA);
  
  // Wait for WiFi to initialize
  delay(100);
  
  // Print MAC Address
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());
}

void loop() {
  // No action needed in loop
}