import firebase_admin
from firebase_admin import credentials, db
import json
import time
import numpy as np
from filterpy.kalman import KalmanFilter
from calc import TrilaterationController

# ==== Firebase Credential Paths ====
RSSI_CRED_PATH = "U:/IPS Project/IPS Project WIFI/Server/rssi-input.json"
POSITION_CRED_PATH = "U:/IPS Project/IPS Project WIFI/Server/ips-phase-1.json"

# ==== AP Configuration ====
AP1_POS = (591, 740)
AP2_POS = (714, 438)
AP3_POS = (489, 569)

# ==== Kalman Filter ====
UNCERTAINTY = 0.5

def init_kf():
    kf = KalmanFilter(dim_x=1, dim_z=1)
    kf.x = np.array([0.0])
    kf.F = np.array([[1.0]])
    kf.H = np.array([[1.0]])
    kf.P *= 100.0
    kf.R = UNCERTAINTY # type: ignore
    return kf

def apply_kalman_filter(kf, value):
    kf.predict()
    kf.update(np.array([value]))
    return kf.x[0]

# ==== Firebase Initialization ====
cred_rssi = credentials.Certificate(RSSI_CRED_PATH)
app_rssi = firebase_admin.initialize_app(cred_rssi, {
    'databaseURL': 'https://rssi-input-default-rtdb.asia-southeast1.firebasedatabase.app/'
}, name='rssi')

cred_pos = credentials.Certificate(POSITION_CRED_PATH)
app_pos = firebase_admin.initialize_app(cred_pos, {
    'databaseURL': 'https://ips-phase-1-default-rtdb.asia-southeast1.firebasedatabase.app/'
}, name='position')

# ==== Trilateration Setup ====
trilateration = TrilaterationController(
    AP1_POS, AP2_POS, AP3_POS,
    measured_power_1=-17,
    measured_power_2=-17,
    measured_power_3=-17,
    path_loss_exponent=1.692,
)

kf_cart_filters = {}

def process_rssi_and_upload():
    rssi_ref = db.reference("/Location_DMIE_Ground", app=app_rssi)
    pos_ref = db.reference("/Location_DMIE_Ground_Positions", app=app_pos)
    raw_data = rssi_ref.get()

    if not raw_data:
        print("No RSSI data found.")
        return

    # List of expected carts
    expected_carts = ["Cart1", "Cart2"]

    for cart_id in expected_carts:
        ap_data = raw_data.get(cart_id) # type: ignore

        if ap_data is None:
            print(f"[{cart_id}] No data found.")
            pos_ref.child(cart_id.lower()).set({"x": 0, "y": 0})
            continue

        try:
            rssi_vals = [ap_data.get("AP1", -999), ap_data.get("AP2", -999), ap_data.get("AP3", -999)]

            if all(val == -999 for val in rssi_vals):
                print(f"[{cart_id}] Offline (all AP RSSI = -999)")
                pos_ref.child(cart_id.lower()).set({"x": 0, "y": 0})
                continue

            # Initialize Kalman filters if needed
            if cart_id not in kf_cart_filters:
                kf_cart_filters[cart_id] = [init_kf(), init_kf(), init_kf()]

            filtered = [
                apply_kalman_filter(kf_cart_filters[cart_id][i], rssi_vals[i])
                for i in range(3)
            ]

            x, y = trilateration.get_position(filtered[0], filtered[1], filtered[2])
            scaled_x = int(x * 20.5)
            scaled_y = int(y * 22)

            pos_ref.child(cart_id.lower()).set({"x": scaled_x, "y": scaled_y})
            print(f"[{cart_id}] RSSI: {rssi_vals} → Position: ({scaled_x}, {scaled_y})")

        except Exception as e:
            print(f"[{cart_id}] Error: {e}")
            pos_ref.child(cart_id.lower()).set({"x": 0, "y": 0})

if __name__ == "__main__":
    while True:
        process_rssi_and_upload()
        time.sleep(1)
