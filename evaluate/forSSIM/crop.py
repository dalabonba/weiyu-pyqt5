import cv2
import numpy as np

def crop_to_mask(original_image_path, mask_path):
    """
    根據遮罩圖裁剪原始圖片,只保留與遮罩圖重疊的區域。
    並在原圖上標出遮罩的邊界框,但不會保存在最終圖像中。
    
    Parameters:
    original_image (numpy.ndarray): 原始圖片
    mask (numpy.ndarray): 遮罩圖（0表示要保留的區域,1表示要移除的區域）
    
    Returns:
    numpy.ndarray: 裁剪後的圖片
    """
    # 讀取圖片
    original_image = cv2.imread(original_image_path)
    mask = cv2.imread(mask_path, 0)

    # 確保遮罩和原圖大小相同
    if original_image.shape[:2] != mask.shape[:2]:
        mask = cv2.resize(mask, (original_image.shape[1], original_image.shape[0]))
    
    # 找到遮罩的邊界框
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = cv2.boundingRect(contours[0])
    
    # 根據邊界框裁剪原始圖片
    cropped_image = original_image[y:y+h, x:x+w]
    
    # 複製一份原始圖片以在上面畫框
    marked_image = original_image.copy()
    
    # 在複製的原始圖上畫出遮罩的邊界框
    cv2.rectangle(marked_image, (x, y), (x+w, y+h), (0, 0, 255), 2)
    
    return cropped_image, marked_image

# if __name__ == "__main__":    
#     original_image = r"C:\Users\upup5\Desktop\research\2_DGTS-Inpainting\logs\my_model_test01\data0025_r.jpg"
#     mask = r"C:\Users\upup5\Desktop\research\2_DGTS-Inpainting\data\mask_teeth_seem_inlay\data0025.png"

#     cropped_image, marked_image = crop_to_mask(original_image, mask)

#     cv2.imshow('Cropped Image', cropped_image)
#     cv2.imshow('Original Image with Mask', marked_image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

#     cv2.imwrite('cropped_image.jpg', cropped_image)