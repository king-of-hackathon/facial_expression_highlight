import os

import cv2
import numpy as np
import torch
from moviepy.editor import VideoFileClip

from .config import Config
from .facial_expression_recognition.network import network
from .person_reid_youtureid.youtureid import YoutuReID


def extract_person_from_image(model, image):
    """ 入力の画像から人を切り抜く

    Args:
        image: 入力画像

    Returns:
        入力画像に写っている人々
    """
    results = model(image)
    bbox = results.xyxy[0].detach().cpu().numpy()

    gallary_image_list = []
    for preds in bbox:
        pos1 = (int(preds[0]), int(preds[1]))
        pos2 = (int(preds[2]), int(preds[3]))
        type = int(preds[5])
        if type == Config.PERSON:
            left, top = pos1
            right, bottom = pos2
            
            crop_image = image[top:bottom, left:right]
            crop_image = cv2.resize(crop_image, Config.youtureid_input_size)
            # リスト追加
            gallary_image_list.append(crop_image)
    return gallary_image_list

def extract_face_from_person(image):
    """入力の人の画像から顔を切り抜く

    Args:
        image: 入力画像

    Returns:
        画像に写っている顔
    """
    for cascade_file in Config.cascade_files:
        clf = cv2.CascadeClassifier(cascade_file)
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_list = clf.detectMultiScale(img_gray)

        for (x, y, w, h) in face_list:
            img = image[y:y + h, x:x + w]
            img = cv2.resize(img, dsize=(150, 150))
            return img

        if len(face_list) != 0:
            return 

class Highlight_Generator:
    def __init__(self, video_name, target_image_name, save_dir):
        self.save_dir = save_dir

        video_path = os.path.join(self.save_dir, video_name)
        self.cap = cv2.VideoCapture(video_path)
        self.original_video_path = video_path
        assert self.cap.isOpened()

        target_image_path = os.path.join(self.save_dir, target_image_name)
        self.target_person = cv2.imread(target_image_path)

    def get_bestshot_frames(self, top=10):
        """ 人物再特定部 

        入力の動画からベストショットのフレームを切り抜く

        Args:
            query_image: 入力画像
            top: 入力画像

        Returns:
            画像に写っている顔
        """
        # query_imageに写っている人物を動画内から再特定する
        query_image = cv2.resize(self.target_person, Config.youtureid_input_size)
        query_image_list = [query_image]
        # AIモデル
        yolov5s = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        yolov5s.eval()
        yolov5s.to(Config.USE_DEVICE)

        youtureid = YoutuReID(
            modelPath=Config.youtureid_model_path,
            backendId=cv2.dnn.DNN_BACKEND_OPENCV,
            targetId=cv2.dnn.DNN_TARGET_CPU,
        )

        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        total_time = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)
        time = 0
        faces = []
        times = []
        while time < total_time:
            # 動画1秒毎にフレームを取得する
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, time*fps)
            is_success, frame = self.cap.read()
            if not is_success:
                break
            # frameから人を抜き出す
            gallery_image_list = extract_person_from_image(yolov5s, frame)
            # frameから抜き出した人を再特定する
            top_topk_value, top_topk_index = youtureid.query(query_image_list, gallery_image_list, topK=1)
            # 閾値以上であれば、その人物であるとする
            if top_topk_value >= Config.re_identification_threshold:
                target_person = gallery_image_list[top_topk_index]
                # 表情認識のために顔の部分を切り取る
                target_person_face = extract_face_from_person(target_person)
                if target_person_face is not None:
                    faces.append(target_person_face)
                    times.append(time)
                    time += 4
            time += 1
            yield int(min(time / total_time, 1.0) * 80)

        # 表情認識部
        if len(faces) == 0:
            return ""
        model = network()
        faces = np.array(faces)
        pred = model.predict(faces)
        bestshot_idxes = np.argsort(pred[:, Config.class_to_idx["Smile"]])[::-1][:top]
        self.highlight_times = np.array(times)[bestshot_idxes]
        yield 85
    
    def create_highlight_video(self):
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_time = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)

        self.videolist = []
        n_hightligh_times = len(self.highlight_times)
        for id, highlight_time in enumerate(self.highlight_times, 1):
            # 出力動画のファイル名
            highlight_video_name  = f"highlight_No{id}.mp4"
            highlight_video_path = os.path.join(self.save_dir, highlight_video_name)
            # 抽出したいフレームorフレーム時間
            start = int(max(highlight_time - 5, 0))
            end = int(min(highlight_time + 5, total_time))
            video = VideoFileClip(self.original_video_path).subclip(start, end)
            video.write_videofile(highlight_video_path,fps=fps)

            self.videolist.append(highlight_video_name)
            yield 90 + int(id / n_hightligh_times * 10)
        yield 100
    
    def __del__(self):
        self.cap.release()