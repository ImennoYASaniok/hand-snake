"""
camera.py - модуль для обработки всего потока камеры, распознавания и детекции движений и жестов руки.

Содержит класс Camera для работы с MediaPipe Hands и вспомогательные функции, которые обрисовывают скелет руки,
визуализируют распознавание и детекцию движений и жестов руки, накладывают спрайты.
"""

import mediapipe as mp
import cv2
from enum import Enum
import numpy as np

from utils import BGR_COLOR_BASE, BGR_COLOR_BACK
from utils import check_press_button


class HandTracker:
    """
    Детектит руку, получает её кординаты и другие параметры

    Attributes:
    """

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hand_detector = self.mp_hands.Hands()
        # self.hands = self.mp_hands.Hands(
        #     static_image_mode=False,
        #     model_complexity=1,
        #     min_detection_confidence=0.75,
        #     min_tracking_confidence=0.75,
        #     max_num_hands=2
        # )

        self.mp_results = None


    def check_detect_hand(self) -> bool:
        if self.mp_results is None: return False
        else: return self.mp_results.multi_hand_landmarks

    def detect(self, frame: np.ndarray):
        self.mp_results = self.hand_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


class DetectMoveType(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    NONE = None

class DataHandler:
    """
    Обрабатывает данные, детектирует жесты и движение руки после получения координат и атрибутах о руке из HandTracker

    Attributes:
    """

    def __init__(self):
        """
        Инициализация параметров, переменных и констант для обработки и детекции
        """

        HAND_POINT_EMPTY_VAL = None
        self.HAND_POINT_EMPTY = [HAND_POINT_EMPTY_VAL, HAND_POINT_EMPTY_VAL]
        self.hand_point = [HAND_POINT_EMPTY_VAL, HAND_POINT_EMPTY_VAL]
        self.cashed_hand_point = []
        self.HAND_POINT_ITER_DIFF = 3
        self.hand_point_flag = False

        self.DETECT_MOVE_LENGTH = 80
        self.detect_move_type = DetectMoveType.NONE

        self.check_touch_4_8 = False
        self.flag_touch_4_8 = False
        self.finger_point_4 = [HAND_POINT_EMPTY_VAL, HAND_POINT_EMPTY_VAL]
        self.finger_point_8 = [HAND_POINT_EMPTY_VAL, HAND_POINT_EMPTY_VAL]

        self.DETECT_TOUCH_LENGTH = 30


    def _get_lm_coords(
            self,
            lm,
            frame_w: int, frame_h: int
    ) -> [int, int]:
        return [int(lm.x * frame_w), int(lm.y * frame_h)]


    def check_touch_sign(
            self,
            x1: int, y1: int,
            x2: int, y2: int
    ) -> bool:
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 < self.DETECT_TOUCH_LENGTH


    def _count_hand_point(
            self,
            landmark,
            frame_w: int, frame_h: int
    ):
        if self.check_touch_4_8:
            cnt = 0

            hand_point_sum_x, hand_point_sum_y = 0, 0
            x, y = self._get_lm_coords(landmark[12], frame_w, frame_h)  # средний
            cnt += 1

            hand_point_sum_x += x; hand_point_sum_y += y
            x, y = self._get_lm_coords(landmark[16], frame_w, frame_h)  # безымянный
            cnt += 1

            hand_point_sum_x += x; hand_point_sum_y += y
            hx, y = self._get_lm_coords(landmark[20], frame_w, frame_h)  # мизинец
            cnt += 1

            hand_point_sum_x += x; hand_point_sum_y += y
            self.hand_point = [hand_point_sum_x // cnt, hand_point_sum_y // cnt]


    def _check_start_move(self) -> bool:
        return self.hand_point is not self.HAND_POINT_EMPTY


    def _check_start_cashed_point(self) -> bool:
        return self.hand_point_flag and self._check_start_move()


    def _check_start_detect_move(self) -> bool:
        return check_press_button("q", type_detect="same")


    def detect_touch_finger_4_8(
            self,
            landmark,
            frame_w: int, frame_h: int
    ):
        self.finger_point_4 = self._get_lm_coords(landmark[4], frame_w, frame_h)
        self.finger_point_8 = self._get_lm_coords(landmark[8], frame_w, frame_h)
        cond_check_touch_sign_4_8 = self.check_touch_sign(self.finger_point_4[0], self.finger_point_4[1],
                                                          self.finger_point_8[0], self.finger_point_8[1])
        if cond_check_touch_sign_4_8 and not self.flag_touch_4_8:
            self.flag_touch_4_8 = True
        if not cond_check_touch_sign_4_8 and self.flag_touch_4_8:
            self.check_touch_4_8 = not self.check_touch_4_8
            self.flag_touch_4_8 = False


    def detect_move(self):
        if self._check_start_detect_move():
            dx = self.hand_point[1] - self.cashed_hand_point[-1][1]
            dy = self.hand_point[0] - self.cashed_hand_point[-1][0]
            cond_up = dx < -self.DETECT_MOVE_LENGTH
            cond_down = dx > self.DETECT_MOVE_LENGTH
            cond_left = dy > self.DETECT_MOVE_LENGTH
            cond_right = dy < -self.DETECT_MOVE_LENGTH
            if cond_up and not cond_down and not cond_left and not cond_right:
                self.detect_move_type = DetectMoveType.UP
            elif not cond_up and cond_down and not cond_left and not cond_right:
                self.detect_move_type = DetectMoveType.DOWN
            elif not cond_up and not cond_down and cond_left and not cond_right:
                self.detect_move_type = DetectMoveType.LEFT
            elif not cond_up and not cond_down and not cond_left and cond_right:
                self.detect_move_type = DetectMoveType.RIGHT
            else:
                self.detect_move_type = None


    def _update_hand_point(self):
        if self._check_start_detect_move():
            if self._check_start_move():
                self.cashed_hand_point.insert(0, self.hand_point)
            if self._check_start_cashed_point():
                self.cashed_hand_point.pop(len(self.cashed_hand_point) - 1)

            if len(self.cashed_hand_point) >= self.HAND_POINT_ITER_DIFF and not self.hand_point_flag:
                self.hand_point_flag = True

    def get_hand_attributes(self, mp_results):
        return zip(mp_results.multi_handedness, mp_results.multi_hand_landmarks)

    def processing(self):
        self._update_hand_point()
        self.detect_move()


PATHS = {
    "assets": "sprites/assets",
    "circles": {},
    "move_arrows": {}
}
for name_file in ["base", "extra"]:
    PATHS["circles"][name_file] = f"{PATHS["assets"]}/{name_file}/{name_file}.png"
for name_file in ["up", "down", "left", "right"]:
    PATHS["move_arrows"][name_file] = f"{PATHS["assets"]}/move_arrows/{name_file}.png"

class CameraRenderer:
    """
    Обрабатывает поток камеры и отрисовывает на нём спрайты и другие объекты

    Attributes:
    """

    def __init__(self):
        """
        Инициализация камеры и её атрибутов.
        """

        self.hand_tracker = HandTracker()
        self.data_handler = DataHandler()

        self.mp_draw = mp.solutions.drawing_utils
        self.landmark_spec = self.mp_draw.DrawingSpec(color=BGR_COLOR_BASE, thickness=2, circle_radius=3)
        self.connection_spec = self.mp_draw.DrawingSpec(color=BGR_COLOR_BACK, thickness=2)

        self.cap = cv2.VideoCapture(0)
        # self.cap.set(cv2.CAP_PROP_FPS, 24)


    def set_img(
            self,
            frame: np.ndarray,
            path: str,
            x_inp_start: int, y_inp_start: int,
            width: int | None = None, height: int | None = None, size_scale: float = 1.0,
            alpha: int = 100,
            trace: bool = False
    ) -> np.ndarray:
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None: return frame

        if width is None: width = height if height is not None else img.shape[1]
        if height is None: height = width if width is not None else img.shape[0]
        width = int(round(width * size_scale))
        height = int(round(height * size_scale))

        if x_inp_start is None or y_inp_start is None:
            return frame

        img = cv2.resize(img, (width, height))
        x_transform_start = x_inp_start - width // 2
        y_transform_start = y_inp_start - height // 2
        x_transform_end = x_transform_start + width
        y_transform_end = y_transform_start + height
        x_start = max(x_transform_start, 0)
        y_start = max(y_transform_start, 0)
        x_end = min(x_transform_end, frame.shape[1])
        y_end = min(y_transform_end, frame.shape[0])
        if x_start >= x_end or y_start >= y_end:
            return frame

        dx_start = x_start - x_transform_start
        dy_start = y_start - y_transform_start
        dx_end = dx_start + (x_end - x_start)
        dy_end = dy_start + (y_end - y_start)

        img = img[dy_start:dy_end, dx_start:dx_end]

        if img.shape[2] == 3:
            b, g, r = cv2.split(img)
            a = np.ones_like(b, dtype=float)
        else:
            b, g, r, a = cv2.split(img)
            a = a.astype(float) / 255.0
        a = np.clip(a * (alpha / 100), 0, 1)
        img_overlay = cv2.merge((b, g, r))

        if trace:
            frame = self.draw_trace(frame, self.data_handler.hand_point, self.data_handler.cashed_hand_point[-1], BGR_COLOR_BASE,  img.shape[1] + 5)

        roi = frame[y_start:y_end, x_start:x_end]
        roi[:] = (img_overlay * a[..., None] + roi * (1 - a[..., None])).astype(np.uint8)
        # for c in range(0, 3):
        #     roi[:, :, c] = img_overlay[:, :, c] * a + roi[:, :, c] * (1 - a)
        frame[y_start:y_end, x_start:x_end] = roi

        return frame


    def draw_trace(
            self,
            frame: np.ndarray,
            pt1: [int, int], pt2: [int, int],
            color: (int, int, int),
            thickness: int = 5,
            steps: int = 10
    ) -> np.ndarray:
        overlay = frame.copy()
        x1, y1 = pt1
        x2, y2 = pt2

        for i in range(steps):
            t = i / steps
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            next_x = int(x1 + (x2 - x1) * (t + 1 / steps))
            next_y = int(y1 + (y2 - y1) * (t + 1 / steps))

            alpha = 1 - t
            cv2.line(overlay, (x, y), (next_x, next_y), color, thickness)

            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
            overlay = frame.copy()

        return frame


    def draw(self, frame: np.ndarray) -> np.ndarray:
        if self.data_handler._check_start_cashed_point() and self.data_handler._check_start_detect_move():
                frame = self.set_img(frame, PATHS["circles"]["base"], self.data_handler.hand_point[0], self.data_handler.hand_point[1], size_scale=2, trace=True)

                path_hand_arrow = None
                if self.data_handler.detect_move_type == DetectMoveType.UP:
                    path_hand_arrow = PATHS["move_arrows"]["up"]
                elif self.data_handler.detect_move_type == DetectMoveType.DOWN:
                    path_hand_arrow = PATHS["move_arrows"]["down"]
                elif self.data_handler.detect_move_type == DetectMoveType.LEFT:
                    path_hand_arrow = PATHS["move_arrows"]["left"]
                elif self.data_handler.detect_move_type == DetectMoveType.RIGHT:
                    path_hand_arrow = PATHS["move_arrows"]["right"]
                if path_hand_arrow is not None:
                    self.set_img(frame, path_hand_arrow, frame.shape[1] // 2, frame.shape[0] // 2, size_scale=5, alpha=50)

        return frame


    def get_frame(self) -> np.ndarray:
        error, frame = self.cap.read()

        # frame = cv2.resize(frame, dsize=(1280, 960), interpolation=cv2.INTER_AREA)
        frame = cv2.flip(frame, 1)

        return frame


    def show(self):
        frame = self.get_frame()
        frame_h, frame_w, frame_c = frame.shape

        self.hand_tracker.detect(frame)
        if self.hand_tracker.check_detect_hand():
            for hand_type, hand_lms in self.data_handler.get_hand_attributes(self.hand_tracker.mp_results):
                # if hand_type.classification[0].label == "Right":
                landmark = hand_lms.landmark

                self.data_handler._count_hand_point(landmark, frame_w, frame_h)

                self.mp_draw.draw_landmarks(
                    frame, hand_lms, self.hand_tracker.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.landmark_spec,
                    connection_drawing_spec=self.connection_spec
                )

            self.data_handler.processing()
            frame = self.draw(frame)

        cv2.imshow("Камера", frame)


    def quit(self):
        cv2.destroyAllWindows()