import os
from queue import Queue

import cv2
from flask import (Blueprint, Response, current_app, flash, redirect,
                   render_template, request, send_from_directory, url_for)
from werkzeug.utils import secure_filename

from .camera import Camera
from .config import Config
from .predict_video import Highlight_Generator
from .select_person import get_person_coordinates

gen = Blueprint("generator", __name__, template_folder="templates", static_folder="static", static_url_path="/static/generator")

# ファイルの拡張子が有効かどうか
def is_allowed_file(file_name, allowed_extentions):
    return "." in file_name and file_name.rsplit(".", 1)[1].lower() in allowed_extentions

@gen.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "video" not in request.files:
            flash("ファイルがありません")
            return redirect(request.url)

        video = request.files["video"]
        if video.filename == "":
            flash("ビデオがありません")
            return redirect(request.url)

        if video and is_allowed_file(video.filename, Config.allowed_extentions):
            video_name = secure_filename(video.filename)
            video_path = os.path.join(current_app.config["UPLOAD_FOLDER"], video_name)
            video.save(video_path)
            return url_for('generator.image_file', filename=video_name)
    return render_template("generator/upload.html")

@gen.route("/select_scene", methods=["POST"])
def select_scene():
    if request.method == "POST":
        # 動画を取得する
        video_name = request.form['video_name']
        video_path = os.path.join(current_app.config["UPLOAD_FOLDER"], video_name)

        # 選択された場面の動画の秒数
        selected_time = request.form.get('video_currentTime', type=float)

        # 選択された場面を動画から切り抜く
        camera = Camera(video_path)
        frame = camera.get_frame_from_time(selected_time)
        scene_image_name = "selected_scene.jpg"
        scene_image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], scene_image_name)
        cv2.imwrite(scene_image_path, frame)
        return url_for('generator.select_person', video_name=video_name, scene_image_name=scene_image_name)

@gen.route("/select_person/<video_name>/<scene_image_name>", methods=["GET", "POST"])
def select_person(video_name, scene_image_name):
    if request.method == "GET":
        # 場面を取得する
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], scene_image_name)
        img = cv2.imread(image_path)
        height, width, _ = img.shape

        # 場面から人の座標を取得する
        coordinates = get_person_coordinates(img)
        person_image_list = []
        for id, coordinate in enumerate(coordinates, 1):
            # (pos1:左上, pos2:右下)の座標
            pos1, pos2 = coordinate
            left, top = pos1
            right, bottom = pos2
            # 場面から人を切り抜く
            person_image = img[top:bottom, left:right]
            person_image_name = f"person_{id}.jpg"
            person_image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], person_image_name)
            cv2.imwrite(person_image_path, person_image)
            person_image_list.append((id, person_image_name, (top/height*100, (height-bottom)/height*100, left/width*100, (width-right)/width*100)))
        return render_template("generator/select_person.html", scene_image=scene_image_name, person_image_list=person_image_list)
    elif request.method == "POST":
        # ハイライトしたい人を取得する
        person_id = request.form['person_id']
        person_image_name = f"person_{person_id}.jpg"
        return render_template("generator/progress.html", video_name=video_name, target_person_image_name=person_image_name)

queue = Queue()

def event_stream(queue):
    while True:
        present = queue.get(True)
        sse_event = 'progress-item'
        if present >= 100:
            sse_event = 'last-item'
            present = 100
        yield f"event:{sse_event}\ndata:{present}\n\n"

@gen.route('/stream')
def stream():
    return Response(event_stream(queue), mimetype='text/event-stream')

@gen.route("/uploads/<video_name>/<target_person_image_name>")
def gen_highlight(video_name, target_person_image_name):
    highlight_gen = Highlight_Generator(video_name, target_person_image_name, os.path.join(current_app.config["UPLOAD_FOLDER"]))
    # 動画内でハイライトするフレームを生成する
    gen = highlight_gen.get_bestshot_frames(top=10)
    for percentage in gen:
        queue.put(percentage)

    gen = highlight_gen.create_highlight_video()
    for percentage in gen:
        queue.put(percentage)
    return render_template("generator/show_highlight_video.html", videolist=highlight_gen.videolist)

@gen.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
