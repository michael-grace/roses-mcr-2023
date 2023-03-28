import json
import time
import urllib.error

import pandas as pd

import config

previous_data = {}

while True:
    # read the spreadsheet
    try:
        df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{config.SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Control", dtype='string')
    except urllib.error.URLError:
        time.sleep(30)
        continue

    # turn into a data structure
    current_data = {}
    df = df.fillna("")
    for _, row in df.iloc[:, 14:18].iterrows():
        if row.iloc[0] == "": continue
        current_data[row.iloc[0]] = {
            "audio_url": f"https://audio.ury.org.uk/roses-out-{row.iloc[0]}" if row.iloc[0] != "Broadcast" else "https://audio.ury.org.uk/live-high",
            "player_url": f"https://roses.ury.org.uk/stream/{row.iloc[0]}",
            "id": row.iloc[0],
            "live": row.iloc[3] != "Off Air",
            "event": row.iloc[2] if row.iloc[3] == "Live" else "Coming Up: " + row.iloc[2]
        }
    
    # process any changes
    changes = False
    for k, v in current_data.items():
        if previous_data == {} or v["event"] != previous_data["event"] or v["live"] != previous_data["live"]:
            changes = True

            # RosesLive API request
            ...
    
    try:
        if current_data["broadcast"]["event"] != previous_data["broadcast"]["event"]:
            # BFM Radiotext
            ...
    except KeyError:
        pass

    # save it
    if changes:
        with open("data.json", "w") as f:
            json.dump([v for v in current_data.values()], f) 

    # MCR data
    with open("mcr.txt", "w") as f:
        f.write(str(df.iloc[:,9][10]) + "\n")
        f.write(str(df.iloc[:,9][11]) + "\n")
        f.write(str(df.iloc[:,9][12]))
    # print(df.iloc[:,9])

    # repeat
    time.sleep(30)