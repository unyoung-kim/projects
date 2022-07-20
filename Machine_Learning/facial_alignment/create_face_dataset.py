import os

import cv2
import numpy as np
from tqdm import tqdm
import mediapipe as mp
from skimage.transform import estimate_transform, warp
from PIL import Image


class Miscellaneous:
    def __init__(self, mode: str):
        if mode == "create_face_dataset":
            face_mesh = mp.solutions.face_mesh
            max_num_faces = 1
            self.face_mesh = face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=max_num_faces,
                refine_landmarks=True,
                min_detection_confidence=0.3
            )
            self.landmarks_list = [np.zeros(shape=(478,3))] * max_num_faces
            self.image_name_count = 0
            self.image_size = 256
            os.makedirs("./data/face", exist_ok=True)
    
    def run(self, mode: str):
        function = getattr(self, mode)
        function()
        
    def create_face_dataset(self):
        video_list = ["arcane1.mp4", "arcane2.mp4", "arcane3.mp4", "arcane4.mp4", "arcane6.mp4", "arcane7.mp4", "arcane8.mp4", "arcane9.mp4"]
        
        for video in tqdm(video_list):
            frame_count = 0
            video_path = f"./data/video/{video}"
            assert os.path.isfile(video_path), f"{video_path} is not valid path"

            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    if frame_count > 10:
                        self.get_cropped_images(frame)
                        frame_count = 0
                    else:
                        frame_count += 1
                else:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
    

    def get_cropped_images(self, image: np.ndarray, scale_factor: float=1.7) -> None:
        results = self.face_mesh.process(image)
        if results.multi_face_landmarks == None:
            return
        
        for i in range(len(results.multi_face_landmarks)):
            for j in range(0, len(results.multi_face_landmarks[i].landmark)):
                self.landmarks_list[i][j, 0] = int(results.multi_face_landmarks[i].landmark[j].x * image.shape[1])
                self.landmarks_list[i][j, 1] = int(results.multi_face_landmarks[i].landmark[j].y * image.shape[0])
                self.landmarks_list[i][j, 2] = int(results.multi_face_landmarks[i].landmark[j].z * image.shape[0])

        image = self.align_face(image)

        results = self.face_mesh.process(image)
        if results.multi_face_landmarks == None:
            return
        
        for i in range(len(results.multi_face_landmarks)):
            for j in range(0, len(results.multi_face_landmarks[i].landmark)):
                self.landmarks_list[i][j, 0] = int(results.multi_face_landmarks[i].landmark[j].x * image.shape[1])
                self.landmarks_list[i][j, 1] = int(results.multi_face_landmarks[i].landmark[j].y * image.shape[0])
                self.landmarks_list[i][j, 2] = int(results.multi_face_landmarks[i].landmark[j].z * image.shape[0])

        for landmarks in self.landmarks_list:
            if sum(landmarks[0]) == 0:
                return
            landmarks = landmarks[:, :2]
            
            left = np.min(landmarks[:, 0])
            right = np.max(landmarks[:, 0])
            top = np.min(landmarks[:, 1])
            bottom = np.max(landmarks[:, 1])
            
            size = (right - left + bottom - top) / 2.0 * scale_factor
            h, w, _ = image.shape

            center = np.array([right - (right - left) / 2.0 - 20.0, bottom - (bottom - top) / 2.0 - 20.0])
            src_pts = np.array([[center[0] - size / 2, center[1] - size / 2], [center[0] - size / 2, center[1] + size / 2], [center[0] + size / 2, center[1] - size / 2]])
            dst_pts = np.array([[0, 0], [0, self.image_size - 1], [self.image_size - 1, 0]])
            tform = estimate_transform('similarity', src_pts, dst_pts)
            
            cropped_image = warp(image, tform.inverse, output_shape = (self.image_size, self.image_size))
            cropped_image = cropped_image * 255
            cv2.imwrite(f"./data/face/{self.image_name_count}.jpg", cropped_image)
            self.image_name_count += 1
    
    def align_face(self, image: np.ndarray) -> np.ndarray:
        # Face alignment
        eye_1, eye_2 = self.landmarks_list[0][133], self.landmarks_list[0][362]

        if eye_1[0] > eye_2[0]:
            left_eye = eye_2
            right_eye = eye_1
        else:
            left_eye = eye_1
            right_eye = eye_2

        left_eye_x, left_eye_y = left_eye[0], left_eye[1]
        right_eye_x, right_eye_y = right_eye[0], right_eye[1]

        dY = left_eye_y - right_eye_y
        dX = left_eye_x - right_eye_x
        angle = np.degrees(np.arctan2(dY, dX)) - 180

        # rotate image
        new_img = Image.fromarray(image)
        new_img = np.array(new_img.rotate(angle))

        return new_img


if __name__ == "__main__":
    misc = Miscellaneous("create_face_dataset")
    misc.run("create_face_dataset")