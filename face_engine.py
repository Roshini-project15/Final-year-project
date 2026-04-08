import cv2
import mediapipe as mp
import math
import os
import tempfile
import traceback
import logging
from deepface import DeepFace

class FaceEngine:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
        self.EAR_THRESHOLD = 0.25
        self.CONSECUTIVE_FRAMES = 2 # Increased to reduce false positives
        self.temp_frame_path = os.path.join(tempfile.gettempdir(), "autosystem_blink_frame.jpg")

    def calculate_ear(self, landmarks, width, height):
        def dist(p1, p2):
            return math.hypot((p1.x - p2.x)*width, (p1.y - p2.y)*height)

        # Left Eye
        left_v1 = dist(landmarks[385], landmarks[373])
        left_v2 = dist(landmarks[387], landmarks[380])
        left_h = dist(landmarks[362], landmarks[263])
        left_ear = (left_v1 + left_v2) / (2.0 * left_h) if left_h > 0 else 0

        # Right Eye
        right_v1 = dist(landmarks[160], landmarks[153])
        right_v2 = dist(landmarks[158], landmarks[144])
        right_h = dist(landmarks[33], landmarks[133])
        right_ear = (right_v1 + right_v2) / (2.0 * right_h) if right_h > 0 else 0

        return (left_ear + right_ear) / 2.0

    def verify_student(self, current_frame, student_list):
        """
        Scans current_frame against a list of student model objects.
        Returns the student object if matched, or None.
        """
        cv2.imwrite(self.temp_frame_path, current_frame)
        
        last_dist = 0
        for student in student_list:
            if not student.image: continue
            image_path = os.path.join(self.upload_folder, student.image)
            if not os.path.exists(image_path): continue

            try:
                res = DeepFace.verify(
                    img1_path=self.temp_frame_path,
                    img2_path=image_path,
                    enforce_detection=False,
                    model_name="Facenet",
                    detector_backend="opencv",
                    distance_metric="cosine"
                )
                if res.get("verified", False):
                    return student, res.get("distance", 0)
            except Exception as e:
                logging.error(f"DeepFace error for {student.name}: {traceback.format_exc()}")
        
        return None, 0

    def cleanup(self):
        if os.path.exists(self.temp_frame_path):
            os.remove(self.temp_frame_path)