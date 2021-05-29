from constants import *
from circular_buffer import CircularBuffer
from buffer import Buffer
from streaming_output import StreamingOutput


import time
import cv2
import threading

class RecordingService:
    def __init__(self, output):
        self.output = output
        self.capture = self.setup_capture()
        self.circular_buffer = CircularBuffer(PREVIEW_LENGTH)
        self.is_saving = False
        self.frames_left = POSTVIEW_LENGTH
        self.frames_counter = 0
    
    def setup_capture(self):
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        capture.set(cv2.CAP_PROP_FPS, FPS)
        return capture
        
    
    def get_gray_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

  
    def detect_movement(self, frame1, frame2):     
        delta = cv2.absdiff(frame1, frame2)
        threshold = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        threshold = cv2.dilate(threshold, None)
        return not (threshold == 0).all() 

    
    def run(self):
        last_frame_gray = self.get_gray_frame(self.capture.read()[1])
        start_time = time.time_ns()
        while True:
            frame = self.capture.read()[1]
            
            # to streaming service
            jpeg_frame = cv2.imencode(".jpg", frame)[1].tobytes()
            self.output.set_frame(jpeg_frame)

            # to circular buffer
            self.circular_buffer.add_frame(frame)

            # detecting movement
            frame_gray = self.get_gray_frame(frame)

            if self.detect_movement(frame_gray, last_frame_gray): #movement detected
                self.frames_left = POSTVIEW_LENGTH
                if not self.is_saving:
                    print("Camera: start of saving recoding")
                    self.is_saving = True
                    buffer = Buffer(self.circular_buffer)
                    self.circular_buffer = CircularBuffer(PREVIEW_LENGTH)
                    threading.Thread(target=buffer.save).start()
            else:
                if self.is_saving:
                    self.frames_left -= 1
                    if self.frames_left == 0:
                        self.is_saving = False
                        print("Camera: end of saving recoding")

            # save frames if is saving
            if self.is_saving:
                buffer.add_frame(frame)

            self.frames_counter += 1
            if self.frames_counter == 99:
                lapse_time = time.time_ns() - start_time
                start_time = time.time_ns()
                fps = 100_000_000_000/lapse_time
                print(f"fps: {fps}")
                self.frames_counter = 0

            last_frame_gray = frame_gray

    def __del__(self):
        print("Releaseing camera")
        self.capture.release()

if __name__ == "__main__":
    recording_service = RecordingService(StreamingOutput())
    try:
        recording_service.run()
    except KeyboardInterrupt:
        pass
    