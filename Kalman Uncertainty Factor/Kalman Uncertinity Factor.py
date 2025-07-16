import pandas as pd
import numpy as np

# File path to your RSSI data
file_path = r"url here" # Replace with your actual file path

# Read CSV using semicolon as separator
df = pd.read_csv(file_path, sep=';', header=None, names=['RSSI', 'Distance'])

# Convert RSSI column to numeric (in case it's read as string)
df['RSSI'] = pd.to_numeric(df['RSSI'], errors='coerce')

# Drop any rows where RSSI is missing or invalid
rssi_values = df['RSSI'].dropna()

# Calculate standard deviation and variance
std_dev = np.std(rssi_values)
variance = std_dev ** 2

# Output results
print(f"Standard Deviation of RSSI: {std_dev:.2f}")
print(f"Recommended Kalman Uncertainty Factor (R): {variance:.2f}")
