import cv2
import numpy as np
import os

def process_image_pair(img1, img2_path, output_path):
    img1=cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
    # 讀取第一個影像
    # img1 = cv2.imread(img1, cv2.COLOR_RGB2BGR)

    # 讀取第二個影像
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

    # 提取第二個影像的紅色通道並二值化以獲得邊框
    _, binary_mask = cv2.threshold(img2, 1, 255, cv2.THRESH_BINARY)

    # 找到邊框的輪廓
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 建立一個遮罩圖像
    mask = np.zeros(img2.shape, dtype=np.uint8)

    # 在遮罩上繪製填滿的輪廓
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)

    # 在邊框內尋找深度值為0的像素並將其改為255
    result = img2.copy()
    result[(mask > 0) & (img2 == 0)] = 255


    # 找到從小於220變為255的位置
    start_positions = (result[:, :-1] < 220) & (result[:, 1:] == 255)
    end_positions = (result[:, :-1] == 255) & (result[:, 1:] < 220)

    # 遍歷每一行並將找到的區間設為0
    for row in range(result.shape[0]):
        starts = np.where(start_positions[row])[0]
        ends = np.where(end_positions[row])[0]

        # 保證開始位置和結束位置的數量一致
        if len(starts) == len(ends):
            for start, end in zip(starts, ends):
                result[row, start:end+1] = 0  # 將區間內的值設為0

    #     # 獲取 result 圖像的高度和寬度
    # height, width = result.shape

    # # 使用 for 循環遍歷圖像的每一行。
    # for row in range(height):
    #     above_threshold = False  # 用於標識當前行是否已經進入高於150的區域
    #     start = -1  # 記錄高於150的起始位置

    #     # 使用 for 循環遍歷當前行的每一列。
    #     for col in range(width - 1):  # 減去1以避免越界
    #         # 如果當前像素值大於150且下一個像素為0
    #         if result[row, col]< 220 and result[row, col + 1] == 255:
    #             if not above_threshold:  # 是否已進入高於240的區域
    #                 above_threshold = True
    #                 start = col  # 記錄起始位置

    #         elif result[row, col] == 255 and above_threshold:  # 檢查深度值是否為0
    #             if start != -1:  # 檢查起始點的有效性
    #                 # 尋找終點
    #                 for next_col in range(col + 1, width):
    #                     if result[row, next_col] < 220:  # 檢查深度值是否高於240
    #                         end = next_col  # 記錄終點
    #                         # 填充區間
    #                         result[row, start:end] = np.where(result[row, start:end] == 255, 0, result[row, start:end])
    #                         break  # 找到終點後，退出尋找終點的循環
    #             break  # 找到一對起點和終點後，退出當前行的循環。

#     # 保存結果
    cv2.imwrite(output_path, result)
# folder1 = 'D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/c++bug/Downred/' # 包含第一張圖（紅色邊框）的資料夾
# folder2 = 'D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/c++bug/Down/' # 包含第二張圖（深度圖）的資料夾
# output_folder = 'D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/c++bug/Downfill/' # 輸出結果的資料夾

# # 確保輸出資料夾存在
# if not os.path.exists(output_folder):
#  os.makedirs(output_folder)

# # 遍歷資料夾
# for filename in os.listdir(folder1):
#     if filename.endswith(('.png', '.jpg', '.jpeg')): # 可以根據需要調整檔案類型
#         img1_path = os.path.join(folder1, filename)
#         img2_path = os.path.join(folder2, filename)

#         # 檢查對應的檔案是否存在
#         if os.path.exists(img2_path):
#             output_path = os.path.join(output_folder, filename)
#             process_image_pair(img1_path, img2_path, output_path)
#             print(f"Processed: {filename}")
#         else:
#             print(f"Skipped: {filename} (No matching file in folder2)")

# print("Processing completed.")