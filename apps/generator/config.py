import torch


class Config:
    image_size=150
    # GPUを使うかどうか
    USE_DEVICE = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    # 許可されている動画の拡張子
    allowed_extentions = {'gif', 'mov', 'mp4'}

    # 人物を再特定する
    youtureid_model_path = "./apps/generator/person_reid_youtureid/person_reid_youtu_2021nov.onnx"
    # 画像に写っているのがその人であると判断する閾値
    re_identification_threshold = 0.55
    youtureid_input_size = (128, 256)

    # 画像から人を認識する
    # yolov5における人のlabel
    PERSON = 0

    # 顔を認識する
    cascade_file_path = "./apps/generator/haarcascade_files/haarcascade_{}.xml"
    cascade_files = [
        cascade_file_path.format("frontalface_default"),
        cascade_file_path.format("frontalface_alt"),
        cascade_file_path.format("frontalface_alt2"),
    ]

    # 表情を認識する
    input_size = (150, 150, 3)
    emotion_model_path = "./apps/generator/facial_expression_recognition/emotion_cnn.h5"
    class_to_idx = {
        "Smile": 0,  # 幸福
        "Anger": 1,  # 怒り
        "Neutral": 2,  # ニュートラル
        "Sorrow": 3,  # 悲しみ
        "Surprise": 4,  # 驚き
    }