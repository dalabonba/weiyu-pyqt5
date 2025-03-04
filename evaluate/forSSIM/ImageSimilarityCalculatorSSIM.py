import numpy as np
import cv2
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

def compare_images(image1, image2):
    """
    比較兩張圖片的相似度，支持文件路徑(str/Path)或cv2圖像作為輸入
    
    Parameters:
    image1: str/Path/numpy.ndarray - 第一張圖片的路徑或cv2圖像
    image2: str/Path/numpy.ndarray - 第二張圖片的路徑或cv2圖像
    
    Returns:
    float: 相似度百分比
    """
    # 檢查輸入類型並相應處理
    def process_input(img):
        if isinstance(img, (str, Path)):
            # 如果輸入是路徑(str)或Path物件
            return np.array(Image.open(str(img)).convert('L'))
        elif isinstance(img, np.ndarray):
            # 如果輸入是cv2圖像
            if len(img.shape) == 3:
                # 如果是彩色圖片，轉換為灰度圖
                return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return img
        else:
            raise TypeError("輸入必須是圖片路徑(str/Path)或cv2圖像(numpy.ndarray)")
    
    # 處理兩張圖片
    img1_array = process_input(image1)
    img2_array = process_input(image2)

    # # 使用 Canny 邊緣檢測
    # img1_array = cv2.Canny(img1_array, 0, 80)
    # img2_array = cv2.Canny(img2_array, 0, 80)

    # cv2.imshow('1', img1_array)
    # cv2.imshow('2', img2_array)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    
    # 確保兩張圖片大小相同
    if img1_array.shape != img2_array.shape:
        img2_array = cv2.resize(img2_array, (img1_array.shape[1], img1_array.shape[0]))
    
    # 計算結構相似性指數 (SSIM)
    similarity = ssim(img1_array, img2_array)
    
    # 轉換為百分比
    percentage = similarity * 100
    
    return percentage

# 使用示例
if __name__ == "__main__": # 只有直接執行此檔案時為True
    image1_path = 'C:/Users/upup5/Downloads/fortestpredict/data0430.png'
    image2_path = 'C:/Users/upup5/Downloads/foranswercrop/data0430.png'

    similarity_percentage = compare_images(image1_path, image2_path)
    print(f"SSIM圖片相似度: {similarity_percentage:.2f}%")