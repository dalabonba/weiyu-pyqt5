import os
import cv2

def compare_image_folders(folder1, folder2, output_folder, image_size=(256, 256)):
    """
    比較兩個資料夾中的相同圖片，計算像素差異並輸出到指定資料夾。
    
    :param folder1: 第一個圖片資料夾 (標準答案)
    :param folder2: 第二個圖片資料夾 (測試結果)
    :param output_folder: 差異圖片輸出資料夾
    :param image_size: 重新調整的圖片大小 (預設為 256x256)
    """
    os.makedirs(output_folder, exist_ok=True)
    
    # 過濾有效的圖片副檔名
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    images1 = {f for f in os.listdir(folder1) if os.path.splitext(f)[1].lower() in valid_extensions}
    images2 = {f for f in os.listdir(folder2) if os.path.splitext(f)[1].lower() in valid_extensions}
    
    # 找到共同的圖片
    common_images = images1.intersection(images2)
    
    if not common_images:
        print("沒有找到相同的圖片檔案。")
        return
    
    for image_name in common_images:
        img1_path = os.path.join(folder1, image_name)
        img2_path = os.path.join(folder2, image_name)
        
        img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
        
        if img1 is None or img2 is None:
            print(f"讀取失敗: {image_name}")
            continue
        
        # 調整圖片大小
        img1 = cv2.resize(img1, image_size)
        img2 = cv2.resize(img2, image_size)
        
        # 計算像素差異
        diff = cv2.absdiff(img1, img2)
        
        # 儲存差異圖片
        diff_path = os.path.join(output_folder, f"diff_{image_name}")
        cv2.imwrite(diff_path, diff)
        
        print(f"已儲存差異圖: {diff_path}")
    
    print("比對完成！")

# # 使用範例
# folder1 = 'D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/prdeictdata/evaluted_testdata_answer/'
# folder2 = 'D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/prdeictdata/Ablation_Study_Test2/'
# output_folder = 'D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/compare_pixel/Ablation_Study_Test2'

# compare_image_folders(folder1, folder2, output_folder)