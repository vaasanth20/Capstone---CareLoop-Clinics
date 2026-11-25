"""Task 1.5: add a temperature to each clinic from the free Open-Meteo weather API.

The API gives an hourly forecast. We take the first value (midnight UTC), which is a
stand-in for "temperature at the clinic", not the current weather.

If a clinic's call fails twice, its temperature is left blank. We never invent a value.

Run from the project folder:
    python -m part1_cleaning.step3_enrich_clinics
"""
import pandas as pd
import requests

from common.paths import DATA_DIR, OUTPUT_DIR

API_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 10
ATTEMPTS_PER_CLINIC = 2


def fetch_first_temperature(latitude, longitude):
    """Return (temperature, None) on success, or (None, reason) when every attempt fails."""
    reason = "unknown"
    for _ in range(ATTEMPTS_PER_CLINIC):
        try:
            response = requests.get(
                API_URL,
                params={"latitude": latitude, "longitude": longitude,
                        "hourly": "temperature_2m", "forecast_days": 1},
                timeout=TIMEOUT_SECONDS,
            )
        except requests.exceptions.RequestException as error:
            reason = f"request failed: {type(error).__name__}"
            continue

        if response.status_code != 200:
            reason = f"HTTP status {response.status_code}"
            continue

        try:
            temperatures = response.json()["hourly"]["temperature_2m"]
        except (ValueError, KeyError):
            reason = "reply had no hourly temperature"
            continue

        return temperatures[0], None

    return None, reason


def main():
    clinics = pd.read_csv(DATA_DIR / "clinics.csv")
    temperatures = []
    for _, clinic in clinics.iterrows():
        temperature, reason = fetch_first_temperature(clinic["latitude"], clinic["longitude"])
        if reason:
            print(f"Could not get temperature for {clinic['clinic_name']}: {reason}")
        temperatures.append(temperature)

    clinics["temp_c"] = temperatures
    output_file = OUTPUT_DIR / "clinics_enriched.csv"
    clinics.to_csv(output_file, index=False)
    print(f"Saved {output_file.name}: {clinics['temp_c'].notna().sum()} of {len(clinics)} clinics have a temperature")


if __name__ == "__main__":
    main()
