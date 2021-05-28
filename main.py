from circular_buffer import CircularBuffer
from streaming_service import StreamingService, StreamingOutput
from buffer import Buffer
from constants import *
import time
import cv2
import threading

def get_gray_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    return gray

def detect_movement(frame1, frame2):     
    delta = cv2.absdiff(frame1, frame2)
    threshold = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold, None)
    return not (threshold == 0).all()


if __name__ == "__main__":
    circular_buffer = CircularBuffer(PREVIEW_LENGTH)
    streaming_output = StreamingOutput()
    streaming_service = StreamingService(streaming_output)
    is_saving = False
    frames_left = POSTVIEW_LENGTH

    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    capture.set(cv2.CAP_PROP_FPS, FPS)


    frames_counter = 0
    print("Camera: start of recording")
    try:
        last_frame_gray = get_gray_frame(capture.read()[1])

 
        start_time = time.time_ns()
        while True:
            frame = capture.read()[1]

            # to streaming service
            jpeg_frame = cv2.imencode(".jpg", frame)[1].tobytes()
            streaming_output.set_frame(jpeg_frame)

            # to circular buffer
            circular_buffer.add_frame(frame)

            # detecting movement
            frame_gray = get_gray_frame(frame)

            if detect_movement(frame_gray, last_frame_gray): #movement detected
                frames_left = POSTVIEW_LENGTH
                if not is_saving:
                    print("Camera: start of saving recoding")
                    is_saving = True
                    buffer = Buffer(circular_buffer)
                    circular_buffer = CircularBuffer(PREVIEW_LENGTH)
                    threading.Thread(target=buffer.save).start()
            else:
                if is_saving:
                    frames_left -= 1
                    if frames_left == 0:
                        is_saving = False
                        print("Camera: end of saving recoding")
            
            # save frames if is saving
            if is_saving:
                buffer.add_frame(frame)

            # FPS counter
            frames_counter += 1
            if frames_counter == 99:
                lapse_time = time.time_ns() - start_time
                start_time = time.time_ns()
                fps = 100_000_000_000/lapse_time
                print(f"fps: {fps}")
                streaming_output.set_fps(fps)
                frames_counter = 0

            last_frame_gray = frame_gray
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    print("Camera: end of recording")

    capture.release()