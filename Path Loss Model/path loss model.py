import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Load CSV with semicolon delimiter
data = pd.read_csv("your url", header=None, sep=';')

# Rename columns
data.columns = ['rssi', 'distance']

# Prepare data
rssi_values = data['rssi'].values.reshape(-1, 1)
distances = data['distance'].values
log_distances = np.log10(distances).reshape(-1, 1)

# Linear regression
regressor = LinearRegression()
regressor.fit(log_distances, rssi_values)

# Results
slope = regressor.coef_[0][0]
intercept = regressor.intercept_[0]
n = -slope / 10
rssi_at_1m = intercept

print(f"Estimated path loss exponent (n): {n:.3f}")
print(f"Estimated RSSI at 1 meter (RSSI(d0)): {rssi_at_1m:.2f} dBm")

# Plot
plt.scatter(log_distances, rssi_values, label='Measured RSSI')
plt.plot(log_distances, regressor.predict(log_distances), color='red', label='Fitted Model')
plt.xlabel('log10(Distance in meters)')
plt.ylabel('RSSI (dBm)')
plt.title('Path Loss Model: RSSI vs log10(Distance)')
plt.legend()
plt.grid(True)
plt.show()
