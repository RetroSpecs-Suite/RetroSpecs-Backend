import cv2
print(cv2.__version__)

def test_camera(max_cameras=3):
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera ID {i} is available")
            ret, frame = cap.read()
            if ret:
                print(f"Successfully captured frame from camera {i}")
            else:
                print(f"Could open camera {i} but failed to capture frame")
            cap.release()
        else:
            print(f"No camera found at ID {i}")

test_camera()