IP Camera to Virtual Camera
概要
このプロジェクトは、IPカメラからストリームを取得し、その映像を仮想カメラとして出力するPythonアプリケーションです。HTTP Basic認証を用いてIPカメラにアクセスし、JPEG形式のフレームを仮想カメラに送信します。OpenCVを使用してJPEGフレームをデコードし、PyVirtualCamを用いて仮想カメラに出力します。

主な機能:

IPカメラへの接続とストリーミング映像の取得
仮想カメラへの映像出力
接続が失敗した場合やストリームが終了した場合の自動再接続機能
依存ライブラリ
このプロジェクトは以下のライブラリに依存しています。

PyVirtualCam (MIT License): 仮想カメラの出力に使用しています。
リポジトリ: https://github.com/letmaik/pyvirtualcam
OpenCV (Apache License 2.0): 画像処理ライブラリとして使用しています。
リポジトリ: https://github.com/opencv/opencv
NumPy (BSD License): 画像データの操作に使用しています。
リポジトリ: https://github.com/numpy/numpy
urllib: Python標準ライブラリとして、HTTPリクエストを処理するために使用しています。
これらのライブラリをインストールするには、以下のコマンドを実行してください:

pip install -r requirements.txt
requirements.txt ファイルには以下の依存関係が記載されています:

pyvirtualcam
opencv-python
numpy

インストール方法
リポジトリをクローンします。



git clone https://github.com/yourusername/ip-camera-to-virtual-camera.git
必要な依存ライブラリをインストールします。


pip install -r requirements.txt
config.txt ファイルをプロジェクトディレクトリに作成し、以下のフォーマットでIPカメラの認証情報とURLを記述します。



<username>
<password>
<ip_camera_url>
アプリケーションを実行します。



python main.py
使用方法
config.txt に記載されたIPカメラに接続し、ストリームを取得します。
取得した映像を仮想カメラにリアルタイムで出力します。
接続が失敗した場合やストリームが終了した場合は、自動的に再接続を試みます。
ライセンス
このプロジェクトは、MIT License のもとでライセンスされています。

PyVirtualCam ライセンス (MIT License)
このプロジェクトは、pyvirtualcam を使用しています。
ライセンス: MIT License

OpenCV ライセンス (Apache License 2.0)
このプロジェクトは、opencv-python を使用しています。
ライセンス: Apache License 2.0

NumPy ライセンス (BSD License)
このプロジェクトは、numpy を使用しています。
ライセンス: BSD License

プロジェクト全体のライセンス

MIT License

Copyright (c) [Year] [Your Name or Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
