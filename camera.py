import mediapipe as mp
import cv2
import math

from color import BGR_COLOR_BASE

class Camera:
    def __init__(self):
        super().__init__()

        self.mp_hands = mp.solutions.hands
        self.hand_detector = self.mp_hands.Hands()
        # self.hands = self.mp_hands.Hands(
        #     static_image_mode=False,
        #     model_complexity=1,
        #     min_detection_confidence=0.75,
        #     min_tracking_confidence=0.75,
        #     max_num_hands=2
        # )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        # self.cap.set(cv2.CAP_PROP_FPS, 24)

        self.HAND_POINT_EMPTY_VAL = None
        self.HAND_POINT_EMPTY = [self.HAND_POINT_EMPTY_VAL, self.HAND_POINT_EMPTY_VAL]
        self.hand_point = [self.HAND_POINT_EMPTY_VAL, self.HAND_POINT_EMPTY_VAL]
        self.cash_hand_point = []
        self.HAND_POINT_ITER_DIFF = 3
        self.hand_point_iter = 0

        self.PATH_SPRITE_FOLDER = "sprites/assets"
        self.PATH_HAND_LINE = "hand_line"
        self.PATH_HAND_LINE_CIRCLE = f"{self.PATH_SPRITE_FOLDER}/{self.PATH_HAND_LINE}/circle.png"

        self.SIZE_HAND_LINE_CIRCLE = 25

    def _get_lm_coords(self, lm, frame_w, frame_h) -> list:
        return [int(lm.x * frame_w), int(lm.y * frame_h)]

    def _count_hand_point(self, landmark, frame_w, frame_h):
        hand_point_sum_x, hand_point_sum_y = 0, 0
        x, y = self._get_lm_coords(landmark[8], frame_w, frame_h)  # указательный
        hand_point_sum_x += x; hand_point_sum_y += y
        x, y = self._get_lm_coords(landmark[12], frame_w, frame_h)  # средний
        hand_point_sum_x += x; hand_point_sum_y += y
        x, y = self._get_lm_coords(landmark[16], frame_w, frame_h)  # безымянный
        hand_point_sum_x += x; hand_point_sum_y += y
        hx, y = self._get_lm_coords(landmark[20], frame_w, frame_h)  # мизинец
        hand_point_sum_x += x; hand_point_sum_y += y
        return [hand_point_sum_x // 4, hand_point_sum_y // 4]

    def set_img(self, frame, path: str, x_inp_start, y_inp_start, x_inp_end=None, y_inp_end=None, width=None, height=None, size_scale=1):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if width is None: width = img.shape[1]
        if height is None: height = img.shape[0]
        width *= size_scale
        height *= size_scale

        if x_inp_start is None or y_inp_start is None: return False

        img = cv2.resize(img, (width, height))
        if x_inp_end is None or y_inp_end is None:
            x_transform_start = x_inp_start - width // 2
            y_transform_start = y_inp_start - height // 2
            x_transform_end = x_transform_start + width
            y_transform_end = y_transform_start + height
        else:
            x_transform_start = x_inp_start
            y_transform_start = y_inp_start
            x_transform_end = x_inp_end
            y_transform_end = y_inp_end
        x_start = max(x_transform_start, 0)
        y_start = max(y_transform_start, 0)
        x_end = min(x_transform_end, frame.shape[1])
        y_end = min(y_transform_end, frame.shape[0])
        if x_start >= x_end or y_start >= y_end:
            return False

        dx_start = x_start - x_transform_start
        dy_start = y_start - y_transform_start
        dx_end = dx_start + (x_end - x_start)
        dy_end = dy_start + (y_end - y_start)

        img = img[dy_start:dy_end, dx_start:dx_end]

        b, g, r, a = cv2.split(img)
        a = a / 255.0
        img_overlay = cv2.merge((b, g, r))

        roi = frame[y_start:y_end, x_start:x_end]
        for c in range(0, 3):
            roi[:, :, c] = img_overlay[:, :, c] * a + roi[:, :, c] * (1 - a)
        frame[y_start:y_end, x_start:x_end] = roi

    def draw_trace(self, frame, pt1, pt2, color, thickness=5, steps=10):
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

    def draw(self, frame):
        if self.hand_point_iter > self.HAND_POINT_ITER_DIFF:
            self.cash_hand_point.pop(len(self.cash_hand_point) - 1)
            frame = self.draw_trace(frame, self.hand_point, self.cash_hand_point[-1], BGR_COLOR_BASE, self.SIZE_HAND_LINE_CIRCLE + 5)
            # cv2.line(frame, self.hand_point, self.cash_hand_point[-1], BGR_COLOR_BASE, self.SIZE_HAND_LINE_CIRCLE + 5)

        self.set_img(frame, self.PATH_HAND_LINE_CIRCLE, self.hand_point[0], self.hand_point[1], width=self.SIZE_HAND_LINE_CIRCLE, height=self.SIZE_HAND_LINE_CIRCLE, size_scale=2)

        return frame

    def show(self):
        error, frame = self.cap.read()
        frame_h, frame_w, frame_c = frame.shape
        # frame = cv2.resize(frame, dsize=(1280, 960), interpolation=cv2.INTER_AREA)
        frame = cv2.flip(frame, 1)
        mp_results = self.hand_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if mp_results.multi_hand_landmarks:
            for hand_type, hand_lms in zip(mp_results.multi_handedness, mp_results.multi_hand_landmarks):
                # if hand_type.classification[0].label == "Right":
                landmark = hand_lms.landmark
                self.hand_point = self._count_hand_point(landmark, frame_w, frame_h)

                self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)

            self.hand_point_iter += 1
            self.cash_hand_point.insert(0, self.hand_point)

            frame = self.draw(frame)
            if self.hand_point_iter > self.HAND_POINT_ITER_DIFF:
                dx = self.cash_hand_point[-1][0] - self.hand_point[0]
                dy = self.cash_hand_point[-1][1] - self.hand_point[1]

        cv2.imshow("Камера", frame)

    def quit(self):
        cv2.destroyAllWindows()