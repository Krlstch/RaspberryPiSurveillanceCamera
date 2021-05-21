from circular_buffer import CircularBuffer
from streaming_service import StreamingService, StreamingOutput
import time
import cv2

WIDTH = 640
HEIGHT = 480
FPS = 10

PREVIEW_LENGTH = 30 # in frames
POSTVIEW_LENGTH = 30 # in frames

DIRECTORY = "recordings"


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
    try:
        _, last_frame = capture.read()
        gray1 = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)

 
        start_time = time.time_ns()
        while True:
            _ , frame = capture.read()

            # to streaming service
            jpeg_frame = cv2.imencode(".jpg", frame)[1].tobytes()
            streaming_output.set_frame(jpeg_frame)

            # to circular buffer
            circular_buffer.add_frame(frame)

            # detecting movement
            gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
            
            delta = cv2.absdiff(gray1, gray2)
            threshold = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
            threshold = cv2.dilate(threshold, None)
            if not (threshold == 0).all(): #movement detected
                frames_left = POSTVIEW_LENGTH
                if not is_saving:
                    is_saving = True
                    file_name = time.strftime("%y%m%d%H%M%S", time.localtime())
                    video_writer = cv2.VideoWriter(f"{DIRECTORY}/{file_name}.avi", cv2.VideoWriter_fourcc('M','J','P','G'),
                                                     FPS, (WIDTH, HEIGHT))
                    circular_buffer.save(video_writer)
            else:
                frames_left -= 1
                if frames_left == 0:
                    is_saving = False
            
            # save frames if is saving
            if is_saving:
                video_writer.write(frame)

            # FPS counter
            frames_counter += 1
            if frames_counter == 99:
                lapse_time = time.time_ns() - start_time
                start_time = time.time_ns()
                fps = 100_000_000_000/lapse_time
                #print(f"fps: {fps}")
                streaming_output.set_fps(fps)
                frames_counter = 0

            last_frame, gray1 = frame, gray2
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)


    capture.release()
    cv2.destroyAllWindows()