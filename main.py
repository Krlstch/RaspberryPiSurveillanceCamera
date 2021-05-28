from streaming_output import StreamingOutput
from recording_service import RecordingService

import flask
import threading


app = flask.Flask(__name__, template_folder="resources", static_folder="resources")

@app.route("/")
def index():
    return flask.render_template("video.html")

def gen():
    while True:
        frame = output.get_frame()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/stream.mjpg')
def video_feed():
    return flask.Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    output = StreamingOutput()
    recording_service = RecordingService(output)
    threading.Thread(target=recording_service.run, daemon=True).start()

    app.run(host="0.0.0.0")
    