import cv2
import numpy as np

def combine_images_with_text(images, texts, output_path=None, top_padding=50, bottom_padding=50):
    """
    合併多張圖片並在每張圖片上添加文字，支援在頂部和底部添加額外文字
    
    參數:
    images: 圖片列表，每個元素都是 numpy.ndarray
    texts: 要添加的文字列表（必須比圖片數量多二個，第一個是頂部文字，最後一個是底部文字）
    output_path: 輸出圖片的路徑（可選）
    top_padding: 頂部文字的預留空間（預設 50 像素）
    bottom_padding: 底部文字的預留空間（預設 50 像素）
    
    返回:
    combined_image: 合併後的圖片 (numpy.ndarray)
    """
    if not images or not isinstance(images, list):
        raise ValueError("images 必須是非空的圖片列表")
    
    if len(texts) != len(images) + 2:  # 需要比圖片數量多兩個文字
        raise ValueError("文字數量必須比圖片數量多二個（頂部和底部文字）")
    
    # 計算合併後圖片的尺寸
    max_height = max(img.shape[0] for img in images)
    total_width = sum(img.shape[1] for img in images)
    
    # 創建一個新的畫布（加上頂部和底部文字的空間）
    combined_image = np.zeros((max_height + top_padding + bottom_padding, total_width, 3), dtype=np.uint8)
    
    # 設定文字參數
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_color = (0, 0, 255)  # 紅色
    thickness = 2
    
    # 添加頂部文字
    top_text = texts[0]  # 第一個文字作為頂部文字
    text_size = cv2.getTextSize(top_text, font, font_scale, thickness)[0]
    text_x = (total_width - text_size[0]) // 2  # 置中
    text_y = top_padding - 20  # 在頂部空間置中
    
    cv2.putText(combined_image, top_text, (text_x, text_y), 
                font, font_scale, font_color, thickness)
    
    # 合併圖片並添加文字
    current_x = 0
    for i, (img, text) in enumerate(zip(images, texts[1:-1])):  # 使用中間的文字
        # 確保圖片是 3 通道的
        if len(img.shape) == 2:  # 如果是灰階圖片
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
        # 將圖片放到新畫布上（注意要考慮頂部padding）
        h, w = img.shape[:2]
        combined_image[top_padding:top_padding+h, current_x:current_x+w] = img
        
        # 計算圖片下方文字位置
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = current_x + (w - text_size[0]) // 2
        text_y = top_padding + h - 20  # 距離圖片底部 20 像素
        
        # 添加圖片文字
        cv2.putText(combined_image, text, (text_x, text_y), 
                    font, font_scale, font_color, thickness)
        
        current_x += w
    
    # 添加底部文字
    bottom_text = texts[-1]  # 最後一個文字作為底部文字
    text_size = cv2.getTextSize(bottom_text, font, font_scale, thickness)[0]
    text_x = (total_width - text_size[0]) // 2  # 置中
    text_y = max_height + top_padding + bottom_padding - 20  # 在底部空間置中
    
    cv2.putText(combined_image, bottom_text, (text_x, text_y), 
                font, font_scale, font_color, thickness)
    
    # 如果提供輸出路徑，就儲存圖片
    if output_path:
        cv2.imwrite(output_path, combined_image)
    
    return combined_image