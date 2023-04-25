import datetime
import json
import pathlib
import time

import requests

from flask import Flask, render_template, abort

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

last_data_read_time = 0
last_data_read = {}

@app.route("/")
def list_streams():
    return render_template("list.html", streams=data())

@app.route("/stream/<stream_id>")
def listen_page(stream_id):
    try:
        stream = [x for x in data() if x["id"] == stream_id][0]
        if not stream["live"]:
            return "this stream is not live at the moment - try another one :)"
        return render_template("player.html", stream=[x for x in data() if x["id"] == stream_id][0])
        
    except IndexError:
        abort(404)

@app.route("/catchup/<catchup_id>")
def catchup_page(catchup_id):
    recordings = requests.get("https://stream-recorder.ury.org.uk/recordings-json").json()
    name = ""
    for recording in recordings:
        if recording["ID"] == catchup_id:
            name = recording["Name"]
            break
    if name != "":
        return render_template("catchup.html", id=catchup_id, name=name)
    else:
        abort(404)

@app.route("/mcr")
def mcr():
    mtime = datetime.datetime.fromtimestamp(pathlib.Path("mcr.txt").stat().st_mtime).strftime("%H:%M:%S")
    with open("mcr.txt") as f:
        mcr_op = f.readline()
        mcr_contact = f.readline()
        mcr_status = f.readline()

    return f"""
    <html style="font-family: Arial">
    <p>Updated at: {mtime}</p>
    <b>MCR Op:</b>
    <p>{mcr_op}</p>
    <b>MCR Contact:</b>
    <p>{mcr_contact}</p>
    <b>MCR Status:</b>
    <p>{mcr_status}</p>
    </html>"""

@app.route("/data")
def data():
    global last_data_read_time
    global last_data_read
    if time.time() - last_data_read_time > 60:
        with open("data.json") as f:
            last_data_read = json.load(f)
        last_data_read_time = time.time()
    return last_data_read

if __name__ == '__main__':
    app.run("0.0.0.0")