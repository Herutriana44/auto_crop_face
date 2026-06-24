import cv2
import numpy as np
import mediapipe as mp
import os
import uuid
import zipfile
from PIL import Image

mp_face_detection = mp.solutions.face_detection


class FaceCropper:
    def __init__(self, min_detection_confidence=0.5):
        self.face_detection = mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=min_detection_confidence
        )

    def detect_faces(self, image_rgb):
        results = self.face_detection.process(image_rgb)
        faces = []
        if results.detections:
            h, w = image_rgb.shape[:2]
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x_min = int(bbox.xmin * w)
                y_min = int(bbox.ymin * h)
                box_w = int(bbox.width * w)
                box_h = int(bbox.height * h)
                faces.append({
                    'x': x_min,
                    'y': y_min,
                    'width': box_w,
                    'height': box_h,
                    'score': detection.score[0]
                })
        return faces

    def crop_face_with_padding(self, image, face, padding_factor=1.5):
        h, w = image.shape[:2]
        cx = face['x'] + face['width'] / 2
        cy = face['y'] + face['height'] / 2
        padded_w = face['width'] * padding_factor
        padded_h = face['height'] * padding_factor

        x1 = max(0, int(cx - padded_w / 2))
        y1 = max(0, int(cy - padded_h / 2))
        x2 = min(w, int(cx + padded_w / 2))
        y2 = min(h, int(cy + padded_h / 2))

        return image[y1:y2, x1:x2]

    def process_image(self, image_path, output_dir, padding_factor=1.5):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Tidak dapat membaca gambar: {image_path}")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = self.detect_faces(image_rgb)

        results = []
        basename = os.path.splitext(os.path.basename(image_path))[0]

        for i, face in enumerate(faces):
            cropped = self.crop_face_with_padding(image, face, padding_factor)
            filename = f"{basename}_face_{i}.jpg"
            out_path = os.path.join(output_dir, filename)
            cv2.imwrite(out_path, cropped, [cv2.IMWRITE_JPEG_QUALITY, 95])
            results.append({
                'filename': filename,
                'score': round(face['score'], 3),
                'size': cropped.shape[:2]
            })

        return results

    def process_video(self, video_path, output_dir, padding_factor=1.5, fps_sample=1):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Tidak dapat membuka video: {video_path}")

        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = max(1, int(video_fps / fps_sample))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        all_results = []
        frame_idx = 0
        processed = 0
        max_frames = min(total_frames, 300)

        while processed < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                faces = self.detect_faces(frame_rgb)

                for j, face in enumerate(faces):
                    cropped = self.crop_face_with_padding(frame, face, padding_factor)
                    filename = f"frame_{frame_idx:04d}_face_{j}.jpg"
                    out_path = os.path.join(output_dir, filename)
                    cv2.imwrite(out_path, cropped, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    all_results.append({
                        'filename': filename,
                        'frame': frame_idx,
                        'score': round(face['score'], 3),
                        'size': cropped.shape[:2]
                    })

                processed += 1

            frame_idx += 1

        cap.release()
        return all_results

    def create_zip(self, output_dir, zip_name="cropped_faces.zip"):
        zip_path = os.path.join(output_dir, zip_name)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(os.listdir(output_dir)):
                if f.endswith(('.jpg', '.png', '.jpeg')):
                    zf.write(os.path.join(output_dir, f), f)
        return zip_path

    def close(self):
        self.face_detection.close()
