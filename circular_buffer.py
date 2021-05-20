class CircularBuffer:
    def __init__(self, size=300):
        self.size = size
        self.buffer = [None for _ in range(size)]
        self.start = 0

    def add_frame(self, frame):
        self.buffer[self.start] = frame
        self.start = (self.start + 1) % self.size
        
    def save(self, video_writer): 
        i = self.start 
        while True:
            if self.buffer[i] is not None:
                video_writer.write(self.buffer[i])


            i = (i+1) % self.size
            if i == self.start:
                break
