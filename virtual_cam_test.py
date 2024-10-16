import os
import sys
import cv2
import numpy as np
from urllib.request import build_opener, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler
import pyvirtualcam
from pyvirtualcam import PixelFormat
import time
import urllib.error

# スクリプトのディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
config_path = os.path.join(script_dir, 'config.txt')

# 認証情報とURLをテキストファイルから読み込む
with open(config_path, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()
    username = lines[0]
    password = lines[1]
    url = lines[2]

# HTTP Basic認証のハンドラを作成
password_mgr = HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url, username, password)
handler = HTTPBasicAuthHandler(password_mgr)
opener = build_opener(handler)

# 仮想カメラの解像度を設定（IPカメラの解像度に合わせて変更してください）
width = 640
height = 480
fps = 60

def connect_to_stream(opener, url):
    """IPカメラのストリームに接続。失敗した場合は再試行。"""
    while True:
        try:
            print("IPカメラに接続を試みています...")
            stream = opener.open(url)
            print("IPカメラに接続しました。")
            return stream
        except urllib.error.URLError as e:
            print(f"接続失敗: {e.reason}. 5秒後に再試行します...")
            time.sleep(5)
        except Exception as e:
            print(f"予期しないエラーが発生しました: {e}. 5秒後に再試行します...")
            time.sleep(5)

def process_stream(cam, stream):
    """ストリームからデータを取得して仮想カメラに送信。"""
    bytes_data = b''
    while True:
        try:
            chunk = stream.read(1024)
            if not chunk:
                print("ストリームが終了しました。再接続を試みます...")
                return False  # ストリームが終了した場合、Falseを返して再接続を試みる
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8')  # JPEG画像の開始バイト
            b = bytes_data.find(b'\xff\xd9')  # JPEG画像の終了バイト
            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                # JPEGデータをデコードして画像に変換
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    # 仮想カメラにフレームを送信
                    cam.send(img)
                    cam.sleep_until_next_frame()
        except Exception as e:
            print(f"ストリーム処理中にエラーが発生しました: {e}")
            return False  # エラーが発生した場合も再接続を試みる

# メインループ
with pyvirtualcam.Camera(width=width, height=height, fps=fps, fmt=PixelFormat.BGR) as cam:
    print(f'Using virtual camera: {cam.device}')
    while True:
        stream = connect_to_stream(opener, url)  # 接続を確立
        # ストリームが終了またはエラー発生時は再接続
        while not process_stream(cam, stream):
            print("再接続を試みます...")
            stream = connect_to_stream(opener, url)
