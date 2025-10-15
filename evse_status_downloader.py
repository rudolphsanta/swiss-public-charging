import requests
import os
import json
import time
from datetime import datetime, timedelta

# Root folder to store data files (can be updated later)
# ROOT_FOLDER = r"D:\Rudolph\Swiss-EVChg-Data"
ROOT_FOLDER = r"M:\Rudolph\0-Datasets\Switzerland\Swiss-EVChg-Data"

# JSON source
url = "https://data.geo.admin.ch/ch.bfe.ladestellen-elektromobilitaet/status/ch.bfe.ladestellen-elektromobilitaet.json"

# Get the next time aligned to a 5-minute mark
def get_next_time(MIN=5):
    """
    Returns a Unix timestamp for the next time that ends in 0 or 5 minutes, offset by 30 seconds.
    """
    now = datetime.now().replace(second=0, microsecond=0)
    minute = now.minute
    next_minute = (minute // MIN + 1) * MIN
    if next_minute >= 60:
        next_time = (now + timedelta(hours=1)).replace(minute=0)
    else:
        next_time = now.replace(minute=next_minute)

    # Add 30 seconds offset
    next_time = next_time + timedelta(seconds=30)
    
    return next_time.timestamp()

# Main loop
def run_collector_loop(interval_minutes=5):
    # Wait until the first aligned run time before starting
    next_run_time = get_next_time(MIN=interval_minutes)
    sleep_duration = next_run_time - time.time()
    if sleep_duration > 0:
        time.sleep(sleep_duration)
        
    while True:
        now = datetime.now()
        
        # Try to download and save the JSON
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
        except Exception as e:
            print(f"[{datetime.now()}] Error fetching data: {e}")
            time.sleep(30)
            continue
            
        # Construct subfolder and file name
        subfolder = now.strftime("%Y-%m")
        file_name = now.strftime("data-%Y-%m-%d-%H-%M-%S.json")
        folder_path = os.path.join(ROOT_FOLDER, subfolder)

        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)
      
        # Save to file
        full_file_path = os.path.join(folder_path, file_name)
        with open(full_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(f"[{datetime.now()}] Saved: {full_file_path}")

        # Wait until the next 5-minute aligned time
        next_run_time = get_next_time(MIN=interval_minutes)
        current_time = time.time()
        sleep_duration = next_run_time - current_time

        if sleep_duration > 0: # Wait to collect the next data on the specified time
            time.sleep(sleep_duration)

# Run the script
if __name__ == "__main__":
    run_collector_loop(interval_minutes=5)
