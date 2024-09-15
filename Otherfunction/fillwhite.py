import cv2
import numpy as np
import os


def process_image_pair(img1_path, img2_path, output_path):
 # 讀取影像
 img1 = cv2.imread(img1_path)
 img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

 # 提取紅色通道並二值化以獲得邊框
 red_channel = img1[:,:,2]
 _, binary_mask = cv2.threshold(red_channel, 1, 255, cv2.THRESH_BINARY)

 # 找到邊框的輪廓
 contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

 # 建立一個遮罩圖像
 mask = np.zeros(img2.shape, dtype=np.uint8)

 # 在遮罩上繪製填滿的輪廓
 cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)

 # 在邊框內尋找深度值為0的像素並將其改為255
 result = img2.copy()
 result[(mask > 0) & (img2 == 0)] = 255

 # 保存結果
 cv2.imwrite(output_path, result)

# 設定資料夾路徑
folder1 = './/Prepedgered//Prepedgered//' # 包含第一張圖（紅色邊框）的資料夾
folder2 = './/test0325//Down//' # 包含第二張圖（深度圖）的資料夾
output_folder = './/finish//' # 輸出結果的資料夾

# 確保輸出資料夾存在
if not os.path.exists(output_folder):
 os.makedirs(output_folder)

# 遍歷資料夾
for filename in os.listdir(folder1):
    if filename.endswith(('.png', '.jpg', '.jpeg')): # 可以根據需要調整檔案類型
        img1_path = os.path.join(folder1, filename)
        img2_path = os.path.join(folder2, filename)

        # 檢查對應的檔案是否存在
        if os.path.exists(img2_path):
            output_path = os.path.join(output_folder, filename)
            process_image_pair(img1_path, img2_path, output_path)
            print(f"Processed: {filename}")
        else:
            print(f"Skipped: {filename} (No matching file in folder2)")

print("Processing completed.")