from streaming_output import StreamingOutput
from recording_service import RecordingService

import flask
import threading
import os
from constants import *


app = flask.Flask(__name__, template_folder="resources", static_folder="resources")

@app.route("/")
def start_page():
    return flask.render_template("start_page.html")


@app.route("/video")
def video():
    return flask.render_template("video.html")

def gen():
    while True:
        frame = output.get_frame()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/stream.mjpg')
def video_feed():
    return flask.Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/files")
def files():
    files = [filename for filename in os.listdir(DIRECTORY) if filename.endswith(".avi")]
    return flask.render_template("files.html", len=len(files), files=files)

@app.route("/files/download/<path:path>")
def get_file(path):
    if os.path.isfile(os.path.join(DIRECTORY, path)):
        return flask.send_from_directory(DIRECTORY, path, as_attachment=True)
    else:
        return flask.render_template("error.html", error_message="File not found")


if __name__ == "__main__":
    output = StreamingOutput()
    recording_service = RecordingService(output)
    threading.Thread(target=recording_service.run, daemon=True).start()

    app.run(host="0.0.0.0")
    