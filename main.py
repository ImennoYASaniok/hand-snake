"""
main.py - главный модуль, который запускает всё приложение

Содержит код запуска сеанса работы приложения
"""

import sys
from camera import CameraRenderer
from utils import check_press_button

if __name__ == '__main__':
    camera_render = CameraRenderer()

    while True:
        camera_render.show()
        if check_press_button("esc"):
            break

    camera_render.quit()
    sys.exit()