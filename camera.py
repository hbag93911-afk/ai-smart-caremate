import cv2


class CameraError(RuntimeError):
    pass


class CameraManager:
    def __init__(self, camera_index: int = 0) -> None:
        self.camera_index = camera_index
        self.cap = None

    def start(self) -> None:
        if self.cap is not None and self.cap.isOpened():
            return

        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not self.cap.isOpened():
            self.cap.release()
            self.cap = None
            raise CameraError("카메라를 열 수 없습니다. 웹캠 연결 상태를 확인하세요.")

    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            raise CameraError("카메라가 시작되지 않았습니다.")

        ok, frame = self.cap.read()
        if not ok:
            raise CameraError("카메라 프레임을 읽지 못했습니다.")
        return frame

    def stop(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None
