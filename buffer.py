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
        i = self.circular_buffer.start 
        while True:
            if self.circular_buffer.buffer[i] is not None:
                self.video_writer.write(self.circular_buffer.buffer[i])


            i = (i+1) % self.circular_buffer.size
            if i == self.circular_buffer.start:
                break
        # copy from queue
        try:
            while True:
                frame = self.queue.get(block=True, timeout=2)
                self.video_writer.write(frame)
        except Empty:
            pass
