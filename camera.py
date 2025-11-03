import mediapipe as mp
import cv2
from PIL import Image as img, ImageDraw as img_draw


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

        self.HAND_POINT_VAL_EMPTY = -1
        self.hand_point_8 = [self.HAND_POINT_VAL_EMPTY, self.HAND_POINT_VAL_EMPTY] # указательный
        self.hand_point_12 = [self.HAND_POINT_VAL_EMPTY, self.HAND_POINT_VAL_EMPTY] # средний
        self.hand_point_16 = [self.HAND_POINT_VAL_EMPTY, self.HAND_POINT_VAL_EMPTY] # безымянный
        self.hand_point_20 = [self.HAND_POINT_VAL_EMPTY, self.HAND_POINT_VAL_EMPTY] # мизинец

    def _get_lm_coords(self, lm, frame_w, frame_h) -> list:
        return [int(lm.x * frame_w), int(lm.y * frame_h)]

    def show(self):
        error, frame = self.cap.read()
        frame_h, frame_w, frame_c = frame.shape
        # frame = cv2.resize(frame, dsize=(1280, 960), interpolation=cv2.INTER_AREA)
        frame = cv2.flip(frame, 1)
        mp_results = self.hand_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if mp_results.multi_hand_landmarks:
            for hand_type, hand_lms in zip(mp_results.multi_handedness, mp_results.multi_hand_landmarks):
                if hand_type.classification[0].label == "Right":
                    landmark = hand_lms.landmark
                    self.hand_point_8 = self._get_lm_coords(landmark[8], frame_w, frame_h)
                    self.hand_point_12 = self._get_lm_coords(landmark[12], frame_w, frame_h)
                    self.hand_point_16 = self._get_lm_coords(landmark[16], frame_w, frame_h)
                    self.hand_point_20 = self._get_lm_coords(landmark[20], frame_w, frame_h)

                    cv2.circle(frame, self.hand_point_8, 35, [0, 0, 0], thickness=5)
                    cv2.circle(frame, self.hand_point_12, 35, [255, 0, 0], thickness=5)
                    cv2.circle(frame, self.hand_point_16, 35, [0, 255, 0], thickness=5)
                    cv2.circle(frame, self.hand_point_20, 35, [0, 0, 255], thickness=5)

                self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Камера", frame)

    def quit(self):
        cv2.destroyAllWindows()