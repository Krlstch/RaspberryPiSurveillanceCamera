import threading
import queue

class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.new_frame_present = False
        self.condition = threading.Condition()

    def set_frame(self, frame):
        with self.condition:
            self.frame = frame
            self.new_frame_present = True
            self.condition.notify()
    
    def get_frame(self):
        with self.condition:
            if not self.new_frame_present:
                self.condition.wait()
            return self.frame
            