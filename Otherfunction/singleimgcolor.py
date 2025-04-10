from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import argparse
import json
import base64
import cv2

parser = argparse.ArgumentParser()
parser.add_argument("--model_dir", help="包含导出模型的目录")
parser.add_argument("--input_file", help="输入 PNG 图像文件")
parser.add_argument("--output_file", help="输出 PNG 图像文件")
a = parser.parse_args()


def apply_gan_model(model_dir, input_file, output_file):
    """
    將 GAN 模型應用於輸入圖片，並將結果保存到指定的輸出檔案中。

    參數：
    - model_dir: 模型檔案目錄路徑。
    - input_file: 輸入 PNG 圖片檔案路徑。
    - output_file: 輸出 PNG 圖片檔案路徑。
    """
    
    # 讀取輸入 PNG 圖像檔案的二進制數據
    with open(input_file, "rb") as f:
        input_data = f.read()

    # 創建包含 base64 編碼的輸入數據的字典
    input_instance = dict(input=base64.urlsafe_b64encode(input_data).decode("ascii"), key="0")
    input_instance = json.loads(json.dumps(input_instance))

    # 啟動 TensorFlow 會話
    with tf.Session() as sess:
        # 找到模型目錄中的最新檢查點
        checkpoint_path = tf.train.latest_checkpoint(model_dir)
        
        # 導入模型元圖並從檢查點恢復會話
        saver = tf.train.import_meta_graph(checkpoint_path + ".meta")
        saver.restore(sess, checkpoint_path)

        # 取得輸入和輸出的 tensor 名稱
        input_vars = json.loads(tf.get_collection("inputs")[0].decode())
        output_vars = json.loads(tf.get_collection("outputs")[0].decode())
        input_tensor = tf.get_default_graph().get_tensor_by_name(input_vars["input"])
        output_tensor = tf.get_default_graph().get_tensor_by_name(output_vars["output"])

        # 將輸入數據轉換為 NumPy 陣列並執行推斷
        input_value = np.array(input_instance["input"])
        output_value = sess.run(output_tensor, feed_dict={input_tensor: np.expand_dims(input_value, axis=0)})[0]

    # 創建包含 base64 編碼的輸出數據的字典
    output_instance = dict(output=output_value.decode("ascii"), key="0")

    # 解碼 base64 並將輸出數據寫入指定的檔案
    b64data = output_instance["output"]
    b64data += "=" * (-len(b64data) % 4)
    output_data = base64.urlsafe_b64decode(b64data.encode("ascii"))
    # 將二進制數據轉為圖片（使用 OpenCV）
    nparr = np.frombuffer(output_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)  # 假設是灰階圖

    # 檢查圖片是否成功解碼
    if img is None:
        raise ValueError("無法解碼圖片數據，請檢查 GAN 模型輸出格式！")

    # 過濾像素值小於 20 的部分
    img[img < 20] = 0

    # 將處理後的圖片轉回二進制數據
    _, buffer = cv2.imencode(".png", img)  # 將圖片編碼為 PNG 格式的二進制數據
    output_data_filtered = buffer.tobytes()

    with open(output_file, "wb") as f:
        f.write(output_data_filtered)


