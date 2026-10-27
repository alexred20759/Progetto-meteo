# USEFUL APIs:
# https://api.open-meteo.com/v1/forecast
# https://geocoding-api.open-meteo.com/v1/search

# current: temperatura, vento
# hourly: temperatura, vento
# daily: temperatura_max, temperatura_min, somma precipitazioni

import locale
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

locale.setlocale(locale.LC_ALL, '')

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

FORECAST_DAYS = 7
FIGSIZE = (6, 4)

# 1. From city name to (latitude, longitude)
nome_citta = input("Inserisci nome città: ").strip()
params_geo = {
    "name": nome_citta,
    "count": 5,
    "countryCode": "it",    # or "language"
}
response_geo = requests.get(GEOCODING_URL, params=params_geo)
data_geo = response_geo.json()

# 2. From (latitude, longitude) to meteo info
params_forecast = {
    "latitude": data_geo["results"][0]["latitude"],
    "longitude": data_geo["results"][0]["longitude"],
    "forecast_days": FORECAST_DAYS,
    "current": "temperature_2m,wind_speed_10m",
    "hourly": "temperature_2m,wind_speed_10m",
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
}
response_forecast = requests.get(FORECAST_URL, params=params_forecast)
data_forecast = response_forecast.json()

# 3. DataFrame
df_hourly = pd.DataFrame(data_forecast["hourly"])
df_hourly["time"] = pd.to_datetime(df_hourly["time"])
df_daily = pd.DataFrame(data_forecast["daily"])
df_daily["time"] = pd.to_datetime(df_daily["time"])

times, temps, wind_speeds = df_hourly["time"], df_hourly["temperature_2m"], df_hourly["wind_speed_10m"]
times_daily, precipitation_sums =  df_daily["time"], df_daily["precipitation_sum"]

# 4. Plot
# 4a. Andamento orario della temperatura
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.plot(times, temps, color="tab:red", linewidth=1)
ax.fill_between(times, temps, color="tab:red", alpha=0.2)
ax.set_title("Andamento orario temperatura", fontweight="bold")
ax.set_ylabel("Temperatura (°C)")
ax.grid(linestyle=":", alpha=0.5)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
plt.show()

# 4b. Andamento orario della velocita' vento
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.plot(times, wind_speeds, color="tab:green", linewidth=1)
ax.fill_between(times, wind_speeds, color="tab:green", alpha=0.2)
ax.set_title("Andamento orario velocità vento", fontweight="bold")
ax.set_ylabel("Velocità (km/h)")
ax.grid(linestyle=":", alpha=0.5)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
plt.show()

# 4c. Temperatura massima e minima giornaliera

# 4d. Precipitazioni giornaliere
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.bar(times_daily, precipitation_sums, color="tab:blue", linewidth=1)
ax.set_title("Precipitazioni Giornaliere", fontweight="bold")
ax.set_ylabel("Precipitazioni (mm)")
ax.grid(axis="y", linestyle=":", alpha=0.5)
ax.set_axisbelow(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
plt.show()