import requests
import matplotlib.pyplot as plt
from datetime import datetime
import os
from dotenv import load_dotenv
import matplotlib.dates as mdates
from collections import defaultdict
import numpy as np
import sys
# Load API key

load_dotenv("PROJECT.env")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# City for weather forecast
CITY = "Mumbai"
URL = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"

# Fetch data safely
try:
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print("Request error:", e)
    sys.exit()

if str(data.get("cod")) != "200":
    print("Error fetching data:", data.get("message"))
    sys.exit()

# ----------------------------
# Next 24 hours forecast
# ----------------------------
dates_24, temps_24, hum_24, conds_24 = [], [], [], []
for entry in data["list"][:8]:  # Next 24h (8 intervals)
    dates_24.append(datetime.fromtimestamp(entry["dt"]))
    temps_24.append(entry["main"]["temp"])
    hum_24.append(entry["main"]["humidity"])
    conds_24.append(entry["weather"][0]["main"])

# ----------------------------
# 5-day daily averages
# ----------------------------
daily_data = defaultdict(lambda: {"temps": [], "hum": []})
for entry in data["list"]:
    day = datetime.fromtimestamp(entry["dt"]).date()
    daily_data[day]["temps"].append(entry["main"]["temp"])
    daily_data[day]["hum"].append(entry["main"]["humidity"])

days, avg_temps, avg_hum = [], [], []
for day, vals in daily_data.items():
    days.append(day)
    avg_temps.append(np.mean(vals["temps"]))
    avg_hum.append(np.mean(vals["hum"]))

# ----------------------------
# Plotting
# ----------------------------
plt.figure(figsize=(12, 6))

# --- Subplot 1: Next 24h ---
plt.subplot(1, 2, 1)
plt.plot(dates_24, temps_24, marker='o', color='orange', label="Temp (°C)")
plt.plot(dates_24, hum_24, marker='s', color='blue', label="Humidity (%)")

# Annotate conditions
for i, cond in enumerate(conds_24):
    plt.text(dates_24[i], temps_24[i] + 0.5, cond, fontsize=8, rotation=45, ha='center')

plt.xlabel("Time")
plt.ylabel("Values")
plt.title(f"{CITY} – Next 24 Hours")
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%b %H:%M"))
plt.grid(True)
plt.legend()

# --- Subplot 2: 5-day avg ---
plt.subplot(1, 2, 2)
plt.plot(days, avg_temps, marker='o', color='red', label="Avg Temp (°C)")
plt.plot(days, avg_hum, marker='s', color='green', label="Avg Humidity (%)")

plt.xlabel("Day")
plt.ylabel("Values")
plt.title(f"{CITY} – 5 Day Forecast (Averages)")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()