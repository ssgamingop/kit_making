import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.7):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]
        self.lm_list = []

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        self.lm_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            h, w, c = img.shape
            for id, lm in enumerate(my_hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy])
                if draw and id == 8: # Index finger tip
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        return self.lm_list

    def get_cursor_position(self):
        """Returns the coordinates of the index finger tip (Landmark 8) if available."""
        if self.lm_list and len(self.lm_list) > 8:
            return self.lm_list[8][1], self.lm_list[8][2]
        return None

    def find_distance(self, p1, p2, img=None):
        """Finds distance between two landmarks (indices) or points (tuples)."""
        if isinstance(p1, int) and isinstance(p2, int):
            # Using landmark indices
            if len(self.lm_list) < max(p1, p2): return 0, img, None
            x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
            x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        else:
            # Using coordinates directly
            x1, y1 = p1
            x2, y2 = p2
            
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        
        if img is not None:
             cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
             cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
             return length, img, [x1, y1, x2, y2, cx, cy]
             
        return length, None, None
