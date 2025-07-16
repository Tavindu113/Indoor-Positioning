# Indoor-Positioning
# 🛰️ Indoor Positioning System (IPS) using ESP32, Wi-Fi RSSI & Firebase

This project implements a real-time **Indoor Positioning System** for tracking the location of carts within an indoor environment using **Wi-Fi RSSI**, **ESP32 microcontrollers**, **Firebase Realtime Database**, and a **web-based visualization**.

<img width="1103" height="657" alt="Screenshot 2025-07-16 142122" src="https://github.com/user-attachments/assets/1ff0323c-128c-4d4b-bde4-55cdb8215ff8" />

---

## 📦 Features

- ✅ **Real-time tracking** of multiple mobile carts (e.g., Cart1, Cart2)
- 📶 **RSSI-based trilateration** from 3 out of 4 fixed Wi-Fi APs
- 🧠 **Kalman Filter** for smoothing noisy RSSI signals
- 🔄 Continuous **data sync with Firebase** (bi-directional)
- 🌐 **Web-based dashboard** with interactive indoor map
- 📊 **CSV logging** for Cart1 data (timestamped)
- ⚠️ Automatic **offline detection** when RSSI = -999 for all APs

---

## 🧠 How It Works

1. Each **cart (ESP32)** scans nearby Wi-Fi Access Points and sends their RSSI values to **Firebase (RSSI DB)**.
2. A **Python server** running on a PC reads RSSI data, filters it with Kalman filters, performs **2D trilateration**, and uploads estimated `(x, y)` coordinates to **Firebase (Position DB)**.
3. A **browser-based HTML app** visualizes the real-time cart positions on an indoor floor map.

---

## 🧰 Tech Stack

| Component         | Technology Used               |
|------------------|-------------------------------|
| Microcontroller  | ESP32 / XIAO ESP32-S3 (Arduino) |
| Backend Database | Firebase Realtime Database     |
| Server Processing| Python (Firebase Admin SDK, FilterPy) |
| Frontend         | HTML5, JavaScript, Canvas API  |
| Algorithms       | Kalman Filter + Least Squares Trilateration |

---

## 🗺️ System Architecture


---

## 🛠️ Installation & Setup

### 📍 Hardware

- 2x or more **ESP32 boards**
  - 1 ESP32 per **cart**
  - 3 or 4 ESP32s as **Wi-Fi Access Points**
- Wi-Fi router for transmitting data to Firebase

### 🧑‍💻 Software Setup

#### 🔹 ESP32 Code (Arduino)

- Cart ESP32: scans for APs named `DMIE_Lab_AP1`, `DMIE_Lab_AP2`, etc.
- Sends data like:
```json
{
  "AP1": -42,
  "AP2": -49,
  "AP3": -45,
  "AP4": -999
}


