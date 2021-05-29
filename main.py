from streaming_output import StreamingOutput
from recording_service import RecordingService
from constants import *

import flask
import threading
import os
import time
import zipfile
import io

app = flask.Flask(__name__, template_folder="resources", static_folder="resources")

def gen():
    while True:
        frame = output.get_frame()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def get_creation_time(file):
    t = time.strptime(file[:-4], "%y%m%d%H%M%S")
    s = time.strftime("%H:%M:%S %d.%m.20%y", t)
    return s

@app.route("/")
def start_page():
    return flask.render_template("start_page.html")


@app.route("/video")
def video():
    return flask.render_template("video.html")


@app.route('/stream.mjpg')
def video_feed():
    return flask.Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/files")
def files():
    files = sorted([filename for filename in os.listdir(DIRECTORY) if filename.endswith(".avi")])
    creation_times = [get_creation_time(file) for file in files]
    return flask.render_template("files.html", files=files, creation_times=creation_times)

@app.route("/files/download/<path:path>")
def get_file(path):
    if os.path.isfile(os.path.join(DIRECTORY, path)):
        return flask.send_from_directory(DIRECTORY, path, as_attachment=True)
    else:
        return flask.render_template("error.html", error_message="File not found")

@app.route("/files/delete/<path:path>")
def delete_file(path):
    if os.path.isfile(os.path.join(DIRECTORY, path)):
        os.remove(os.path.join(DIRECTORY, path))
        return flask.redirect("/files")
    else:
        return flask.render_template("error.html", error_message="File not found")

@app.route("/files/download_all")
def get_all_file():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in os.listdir(DIRECTORY):
            if file.endswith(".avi"):
                zip_file.write(os.path.join(DIRECTORY, file))
    buffer.seek(0)
    return flask.send_file(buffer, mimetype="zip", attachment_filename="recordings.zip", as_attachment=True)

@app.route("/files/delete_all")
def delete_all_file():
    for file in os.listdir(DIRECTORY):
        if file.endswith(".avi"):
            os.remove(os.path.join(DIRECTORY, file))
    return flask.redirect("/files")

if __name__ == "__main__":
    app.jinja_env.globals.update(zip=zip)

    output = StreamingOutput()
    recording_service = RecordingService(output)
    threading.Thread(target=recording_service.run, daemon=True).start()

    app.run(host="0.0.0.0")
    