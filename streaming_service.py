import logging
import socketserver
import threading
from http import server

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = StreamingService.page.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with StreamingService.output.frame_condition:
                        StreamingService.output.frame_condition.wait()
                        frame = StreamingService.output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(f'Removed streaming client {self.client_address}: {e}')
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class StreamingService:
    def __init__(self, output):
        self.server = StreamingServer(("", 8000), StreamingHandler)
        StreamingService.output = output
        with open("resources/index.html", "r") as file:
            StreamingService.page = file.read()
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        
class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.fps = 0
        self.frame_condition = threading.Condition()
        self.fps_condition = threading.Condition()

    def set_frame(self, frame):
        with self.frame_condition:
            self.frame = frame
            self.frame_condition.notify_all()
    
    def set_fps(self, fps):
        with self.fps_condition:
            self.fps = fps
            self.fps_condition.notify_all()