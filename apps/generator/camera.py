import cv2


class Camera:
    def __init__(self, video):
        self.cap = cv2.VideoCapture(video)

    def get_frame_from_time(self, time):
        frame_count = time * self.cap.get(cv2.CAP_PROP_FPS)
        error = self.cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1 / self.cap.get(cv2.CAP_PROP_FPS)
        frame_count = min(frame_count, error)
        return self.get_frame(frame_count)

    def get_frame(self, frame_count):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
        success, frame = self.cap.read()
        assert success is True
        return frame

    def __del__(self):
        self.cap.release()
