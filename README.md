# 🛰️ Indoor Positioning System (IPS) using ESP32, Wi-Fi RSSI & Firebase

This project presents a real-time **Indoor Positioning System (IPS)** designed to track mobile carts within an indoor environment using:

- 📶 **Wi-Fi RSSI signals**  
- 🧠 **Kalman filtering** for noise reduction  
- 📡 **ESP32/XIAO ESP32-S3 microcontrollers** as both access points and mobile nodes  
- ☁️ **Firebase Realtime Database** for bidirectional data exchange  
- 🌐 **Web-based HTML dashboard** to visualize cart movement in real time

---

## 📦 Features

- ✅ Real-time tracking of multiple mobile carts (e.g., `Cart1`, `Cart2`)
- 📶 RSSI-based trilateration from 3 out of 4 fixed Wi-Fi Access Points (APs)
- 🧠 Kalman Filter for accurate smoothing of RSSI values
- 🔁 Bi-directional communication with Firebase Realtime DB
- 🖼️ Web dashboard with interactive canvas-based indoor map
- 📊 Automatic CSV logging for historical position data
- ⚠️ Offline cart detection when no APs are reachable

---

## 🧠 How It Works

1. **ESP32 carts** continuously scan for nearby APs (with known SSIDs like `DMIE_Lab_AP1`).
2. RSSI values are sent to **Firebase Input DB** (`rssi-input` project).
3. A **Python server**:
   - Fetches RSSI values from Firebase
   - Applies Kalman filtering
   - Performs trilateration using 3 APs
   - Scales and uploads coordinates to **Firebase Output DB** (`ips-phase-1`)
   - Optionally logs the result to a `.csv` file
4. A **web-based dashboard** reads cart positions and displays them on an indoor map.

---

## 🧰 Tech Stack

| Component         | Technology Used                          |
|------------------|-------------------------------------------|
| Microcontroller  | ESP32 / XIAO ESP32-S3 (Arduino)           |
| Backend Database | Firebase Realtime Database (2 projects)   |
| Server Processing| Python, Firebase Admin SDK, FilterPy      |
| Frontend         | HTML, JavaScript, Canvas API              |
| Algorithms       | Kalman Filter + Trilateration (Least Squares) |

---

## 🗺️ System Architecture

```
+---------------------+       Wi-Fi Scan       +---------------------+
|     ESP32 Cart      |----------------------->|     ESP32 AP Nodes   |
| (Client Node: Cart1)| <--------------------- |   (Fixed Positions)  |
+---------------------+     Signal Strength    +---------------------+

         |
         |    RSSI Data (AP1, AP2, AP3, AP4)
         v
+------------------------+
| Firebase Input DB      |  ← rssi-input
| (/Location_DMIE_Ground)|
+------------------------+

         |
         |    Python Server
         v

+--------------------------+     → Trilateration + Kalman Filter
|  firebase_trilateration.py |
+--------------------------+

         |
         |   Estimated (x, y)
         v

+------------------------+
| Firebase Output DB     |  ← ips-phase-1
| (/Location_DMIE_Ground_Positions)
+------------------------+

         |
         v
+------------------------------+
| Web HTML Map Dashboard       |
| (index.html + Firebase JS)   |
+------------------------------+
```

---

## 🛠️ Installation & Setup

### 🔧 Hardware Requirements

- 1x or more **ESP32 boards** per cart (mobile node)
- 3–4 **ESP32 boards** configured as APs
- 1x Wi-Fi router for Firebase data transmission
- A laptop/PC to run the **Python server**
- Indoor map (scaled) for visualization

---

### 🖥️ Software Setup

#### 1️⃣ ESP32 (Node Code – Arduino IDE)

- Each cart scans for SSIDs:
  - `DMIE_Lab_AP1`, `DMIE_Lab_AP2`, `DMIE_Lab_AP3`, `DMIE_Lab_AP4`
- It connects to a separate Wi-Fi to **upload data to Firebase** (not the APs).
- RSSI values are uploaded in this structure:

```json
{
  "Cart1": {
    "AP1": -52,
    "AP2": -60,
    "AP3": -55,
    "AP4": -999
  }
}
```

📝 `-999` indicates the AP is **not detected**.

> Each cart should use a unique cart ID (`Cart1`, `Cart2`, etc.)

#### 2️⃣ Python Server

- Uses `firebase_admin`, `filterpy`, and `numpy`
- Processes RSSI → `(x, y)` using trilateration
- Logs positions to Firebase and optional `.csv`

Install dependencies:

```bash
pip install firebase-admin filterpy numpy
```

Place your service account files:

- `rssi-input.json` → for RSSI input database
- `ips-phase-1.json` → for position output database

#### 3️⃣ Web Dashboard (HTML + JS)

- Reads from `/Location_DMIE_Ground_Positions`
- Uses Firebase JS SDK (v8)
- Displays cart positions overlaid on indoor map
- Dynamically updates every few seconds

📍 Displays cart location + weight (manually defined) + zoom controls

---

## 📁 Folder Structure

```
├── Server/
│   ├── firebase_trilateration.py
│   ├── calc.py
│   ├── rssi-input.json
│   ├── ips-phase-1.json
│   ├── cart1_log.csv
│   └── ...
├── Nodes/
│   ├── Cart_1.ino
│   ├── Cart_2.ino
│   └── ...
├── Web/
│   ├── index.html
│   └── assets/
```

---

## 🧪 Example Output

```
[Cart1] RSSI: [-43, -48, -41, -999] → Position: (594, 512)
[Cart2] Offline (all AP RSSI = -999)
```

---

## 📌 Notes

- Position `(x, y)` is scaled using a factor (e.g., `20.5`) to map to canvas coordinates
- If all RSSIs are `-999`, the cart is assumed **offline** and its position becomes `(0, 0)`
- The server supports any number of carts as long as they're defined in the RSSI DB

---

## 📸 Web Dashboard Preview

![Screenshot](https://github.com/user-attachments/assets/1ff0323c-128c-4d4b-bde4-55cdb8215ff8)

---

## 📍 Future Improvements

- Multi-floor support
- Signal strength heatmap
- Machine learning for enhanced localization
- MQTT integration for lower latency
