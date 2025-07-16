import firebase_admin
from firebase_admin import credentials, db
import time
import numpy as np
from filterpy.kalman import KalmanFilter
import csv
from datetime import datetime

# === Firebase Credentials ===
RSSI_CRED_PATH = "U:/IPS Project/IPS Project WIFI/Server/rssi-input.json"
POSITION_CRED_PATH = "U:/IPS Project/IPS Project WIFI/Server/ips-phase-1.json"

# === AP Coordinates ===
AP_POSITIONS = [
    (17.85, 21.37),  # AP1
    (28.83, 21.37),  # AP2
    (28.83, 36.10),   # AP3
    (19.00, 36.10)    # AP4
]

# === RSSI to Distance Parameters ===
TX_POWER = -18
PATH_LOSS_EXPONENT = 1.5

# === CSV Log File ===
CSV_LOG_FILE = "cart1_log.csv"
with open(CSV_LOG_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Timestamp", "CartID",
        "RSSI_AP1", "RSSI_AP2", "RSSI_AP3", "RSSI_AP4",
        "X", "Y"
    ])

# === Firebase Setup ===
cred_rssi = credentials.Certificate(RSSI_CRED_PATH)
app_rssi = firebase_admin.initialize_app(cred_rssi, {
    'databaseURL': 'https://rssi-input-default-rtdb.asia-southeast1.firebasedatabase.app/'
}, name='rssi')

cred_pos = credentials.Certificate(POSITION_CRED_PATH)
app_pos = firebase_admin.initialize_app(cred_pos, {
    'databaseURL': 'https://ips-phase-1-default-rtdb.asia-southeast1.firebasedatabase.app/'
}, name='position')

# === 2D Kalman Filter Setup ===
def init_position_kf():
    kf = KalmanFilter(dim_x=4, dim_z=2)
    kf.F = np.array([[1, 0, 1, 0],
                     [0, 1, 0, 1],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]])
    kf.H = np.array([[1, 0, 0, 0],
                     [0, 1, 0, 0]])
    kf.P *= 5000.
    kf.R *= 25.
    kf.Q = np.eye(4)
    kf.x = np.array([0, 0, 0, 0])
    return kf

def update_position_kf(kf, x, y):
    z = np.array([x, y])
    kf.predict()
    kf.update(z)
    return kf.x[0], kf.x[1]

kf_cart_filters = {}

# === RSSI to Distance Conversion ===
def rssi_to_distance(rssi, tx_power, n):
    return 10 ** ((tx_power - rssi) / (10 * n))

# === Least Squares Trilateration ===
def least_squares_position(positions, distances):
    x0, y0 = positions[0]
    d0 = distances[0]
    A, b = [], []
    for i in range(1, len(positions)):
        xi, yi = positions[i]
        di = distances[i]
        A.append([2*(xi - x0), 2*(yi - y0)])
        b.append([d0**2 - di**2 - x0**2 + xi**2 - y0**2 + yi**2])
    A = np.array(A)
    b = np.array(b)
    pos, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    return pos[0][0], pos[1][0]

# === Main Processing ===
def process_rssi_and_upload():
    rssi_ref = db.reference("/Location_DMIE_Ground", app=app_rssi)
    pos_ref = db.reference("/Location_DMIE_Ground_Positions", app=app_pos)
    raw_data = rssi_ref.get()

    if not raw_data:
        print("No RSSI data found.")
        return

    expected_carts = ["Cart1", "Cart2"]

    for cart_id in expected_carts:
        ap_data = raw_data.get(cart_id)

        if ap_data is None:
            print(f"[{cart_id}] No data found.")
            continue

        try:
            rssi_vals = [
                ap_data.get("AP1", -999),
                ap_data.get("AP2", -999),
                ap_data.get("AP3", -999),
                ap_data.get("AP4", -999)
            ]

            if all(val == -999 for val in rssi_vals):
                print(f"[{cart_id}] Offline (all RSSI -999)")
                continue

            # Distance + Position lists
            distances = []
            valid_positions = []
            for i, rssi in enumerate(rssi_vals):
                if rssi == -999:
                    continue
                dist = rssi_to_distance(rssi, TX_POWER, PATH_LOSS_EXPONENT)
                distances.append(dist)
                valid_positions.append(AP_POSITIONS[i])

            if len(distances) < 4:
                print(f"[{cart_id}] Skipping update: fewer than 4 valid APs.")
                continue

            x, y = least_squares_position(valid_positions, distances)
            scaled_x = int(x * 18)
            scaled_y = int(y * 18)

            if scaled_x == 0 and scaled_y == 0:
                print(f"[{cart_id}] Invalid (0,0) position — skipping update.")
                continue

            if cart_id not in kf_cart_filters:
                kf_cart_filters[cart_id] = init_position_kf()

            kf = kf_cart_filters[cart_id]
            smooth_x, smooth_y = update_position_kf(kf, scaled_x, scaled_y)

            pos_ref.child(cart_id.lower()).set({
                "x": int(smooth_x),
                "y": int(smooth_y)
            })

            print(f"[{cart_id}] RSSI: {rssi_vals} → Position: ({int(smooth_x)}, {int(smooth_y)})")

            if cart_id == "Cart1":
                with open(CSV_LOG_FILE, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([
                        timestamp,
                        cart_id,
                        *rssi_vals,
                        int(smooth_x),
                        int(smooth_y)
                    ])

        except Exception as e:
            print(f"[{cart_id}] Error: {e}")

# === Main Loop ===
if __name__ == "__main__":
    while True:
        process_rssi_and_upload()
        time.sleep(1)
