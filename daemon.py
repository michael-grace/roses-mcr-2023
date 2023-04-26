import datetime
import json
import time
import urllib.error

import pandas as pd

import config
import roseslive

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
    
    if previous_data == {}:
        previous_data = current_data


    # process any changes
    changes = False
    for k, v in current_data.items():
        current_data[k]["roseslive_id"] = previous_data[k].get("roseslive_id")
        current_data[k]["start_time"] = previous_data[k].get("start_time")

        if previous_data == {} or v["event"] != previous_data[k]["event"] or v["live"] != previous_data[k]["live"]:
            changes = True

            # RosesLive API request
            if k == "broadcast":
                continue

            if previous_data[k]["live"] and not v["live"]:
                # deal with catchup
                # check the times are reasonable
                # TODO
                if v.get("startTime") is None:
                    continue

                # request from the logger
                log_id = roseslive.request_log(k, datetime.datetime.fromisoformat(v["startTime"]), datetime.datetime.fromisoformat(v["endTime"]), v["event"])
                
                # upload it
                roseslive.change_to_catchup(current_data[k]["roseslive_id"], f"Catch Up: {v['event']}", f"https://roses.ury.org.uk/catchup/{log_id}") 

                continue

            if not previous_data[k]["live"] and v["live"]:
                # publish it
                roseslive_id = roseslive.publish(f"{v['event']} Commentary", v["player_url"], False)

                # save the id and stream start time
                current_data[k]["roseslive_id"] = roseslive_id
                current_data[k]["start_time"] = datetime.datetime.now().astimezone().isoformat()
                continue

            # otherwise, stop the old one, make it catchup and start a new one

            if v.get("startTime") is None:
                    continue

            # request from the logger
            log_id = roseslive.request_log(k, datetime.datetime.fromisoformat(v["startTime"]), datetime.datetime.fromisoformat(v["endTime"]), v["event"])
            
            # upload it
            roseslive_id = roseslive.publish(f"{v['event']} Commentary", v["player_url"], False)

            # save the id and stream start time
            current_data[k]["roseslive_id"] = roseslive_id
            current_data[k]["start_time"] = datetime.datetime.now().astimezone().isoformat()

            # goodness, this is all so dodgy

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
    previous_data = current_data
    time.sleep(30)