import sys
import cv2
from camera import Camera

if __name__ == '__main__':
    camera = Camera()

    while True:
        camera.show()
        if cv2.waitKey(1) == 27:
            break

    camera.quit()
    sys.exit()