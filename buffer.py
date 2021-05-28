from constants import *
from queue import Queue, Empty
import time
import cv2

class Buffer:
    def __init__(self, circular_buffer, size=30):
        self.circular_buffer = circular_buffer
        self.queue = Queue()
        file_name = time.strftime("%y%m%d%H%M%S", time.localtime())
        self.video_writer = cv2.VideoWriter(f"{DIRECTORY}/{file_name}.avi", cv2.VideoWriter_fourcc('M','J','P','G'),
                                            FPS, (WIDTH, HEIGHT))


    def add_frame(self, frame):
        self.queue.put(frame)
        
    def save(self):
        # copy circular buffer
        self.circular_buffer.save(self.video_writer)
        
        # copy from queue
        try:
            while True:
                frame = self.queue.get(block=True, timeout=2)
                self.video_writer.write(frame)
        except Empty:
            pass
