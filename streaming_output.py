import threading
import queue

class StreamingOutput:
    def __init__(self):
        self.queue = queue.Queue(maxsize=1)

    def set_frame(self, frame):
        if self.queue.full():
            self.queue.get()
        self.queue.put(frame)
    
    def get_frame(self):
        return self.queue.get(block=True)
            