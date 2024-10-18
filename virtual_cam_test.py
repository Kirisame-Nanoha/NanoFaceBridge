import os
import sys
import cv2
import numpy as np
import threading
import psutil
import time
from urllib.request import build_opener, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler
import urllib.error
import pyvirtualcam
from pyvirtualcam import PixelFormat

# スクリプトのディレクトリを取得
if getattr(sys, 'frozen', False):
    # PyInstallerでビルドされた実行可能ファイルの場合
    script_dir = os.path.dirname(sys.executable)  # EXEのディレクトリ
else:
    # 通常のPythonスクリプトの場合
    script_dir = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(script_dir, 'config.txt')  # 外部のconfig.txtのパス

# 認証情報とURLをテキストファイルから読み込む
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        username = lines[0]
        password = lines[1]
        url = lines[2]
except Exception as e:
    print(f"設定ファイルの読み込み中にエラーが発生しました: {e}")
    sys.exit(1)

# HTTP Basic認証のハンドラを作成
password_mgr = HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url, username, password)
handler = HTTPBasicAuthHandler(password_mgr)
opener = build_opener(handler)

# 仮想カメラの解像度を設定（IPカメラの解像度に合わせて変更してください）
width = 640
height = 480
fps = 60  # FPSはIPカメラのFPSに合わせてください

# 終了フラグ
exit_flag = threading.Event()

def connect_to_stream(opener, url):
    """IPカメラのストリームに接続。失敗した場合は再試行。"""
    while not exit_flag.is_set():
        try:
            print("IPカメラに接続を試みています...")
            stream = opener.open(url, timeout=10)
            print("IPカメラに接続しました。")
            return stream
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"接続失敗: HTTP Error {e.code}: {e.reason}. 5秒後に再試行します...")
            else:
                print(f"接続失敗: HTTP Error {e.code}: {e.reason}. 5秒後に再試行します...")
            time.sleep(5)
        except Exception as e:
            print(f"接続失敗: {e}. 5秒後に再試行します...")
            time.sleep(5)
    return None

def create_disconnected_frame(width, height):
    """切断時に表示するフレームを作成。"""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, 'Disconnected', (int(width*0.1), int(height*0.5)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame

def process_stream(cam, stream):
    """ストリームからデータを取得して仮想カメラに送信。"""
    bytes_data = b''
    last_frame_mean = None
    no_update_duration = 0
    max_no_update_duration = 5  # フレームが更新されないと判断するまでの秒数
    frame_time = time.time()

    while not exit_flag.is_set():
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
                    current_time = time.time()
                    # フレームの平均値を取得して比較
                    current_mean = img.mean()
                    if last_frame_mean is not None and current_mean == last_frame_mean:
                        no_update_duration += current_time - frame_time
                    else:
                        no_update_duration = 0  # フレームが更新されたらカウンターをリセット
                    frame_time = current_time
                    last_frame_mean = current_mean

                    if no_update_duration >= max_no_update_duration:
                        print("フレームの更新が停止しました。再接続を試みます...")
                        return False  # フレームが更新されていないので再接続

                    # 仮想カメラにフレームを送信
                    cam.send(img)
                    cam.sleep_until_next_frame()
        except Exception as e:
            print(f"ストリーム処理中にエラーが発生しました: {e}")
            return False  # エラーが発生した場合も再接続を試みる
    return False

def monitor_processes():
    """指定されたプロセスを監視し、終了したらプログラムを終了する。"""
    processes_to_monitor = ['nanoface.exe', 'mocap assistant plus.exe']
    processes_running = {name: False for name in processes_to_monitor}

    while True:
        all_exited = True
        for proc_name in processes_to_monitor:
            is_running = any(proc.name().lower() == proc_name for proc in psutil.process_iter())
            if is_running:
                processes_running[proc_name] = True
                all_exited = False
            elif processes_running[proc_name]:
                print(f"{proc_name} が終了しました。プログラムを終了します。")
                exit_flag.set()
                return
            else:
                all_exited = False
        if all_exited:
            print("監視対象のプロセスが見つかりません。")
        time.sleep(5)

# メインループ
def main():
    # プロセス監視スレッドの開始
    monitor_thread = threading.Thread(target=monitor_processes, daemon=True)
    monitor_thread.start()

    with pyvirtualcam.Camera(width=width, height=height, fps=fps, fmt=PixelFormat.BGR) as cam:
        print(f'Using virtual camera: {cam.device}')
        disconnected_frame = create_disconnected_frame(cam.width, cam.height)
        while not exit_flag.is_set():
            stream = connect_to_stream(opener, url)  # 接続を確立
            if stream is None:
                break  # exit_flag が設定されているため終了
            # ストリームが終了またはエラー発生時は再接続
            while not process_stream(cam, stream):
                if exit_flag.is_set():
                    break
                print("再接続を試みます...")
                # 再接続中も切断時のフレームを送信
                cam.send(disconnected_frame)
                cam.sleep_until_next_frame()
                time.sleep(1)  # 再接続前に少し待機
                stream = connect_to_stream(opener, url)
                if stream is None:
                    break
    print("プログラムを終了します。")
    sys.exit(0)

if __name__ == '__main__':
    main()
