from PIL import Image
import os
import numpy as np
# base_folder = "D://Users//user//Desktop//顏唯育-1勿刪//paper//crown//traincode//"
# input_folders = ["test"]
# output_folder_base_prep = "test//Prepedgered"
# output_folder_base_op = "test//Prepedgeyellow"




def get_image_bound(input_image_path, color=(255, 0, 0)):
    # 打開圖像並轉換為灰階
    img = Image.open(input_image_path).convert('L')
    
    # 將圖像轉換為 NumPy 陣列
    img_array = np.array(img)
    
    # 將像素值小於10的地方設為0
    img_array = np.where(img_array >= 10, img_array, 0)
    
    # 創建一個RGB陣列，初始化為黑色
    boundary_img_array = np.zeros((*img_array.shape, 3), dtype=np.uint8)
    
    # 獲取邊界條件，檢查上下左右是否是邊界點
    up_shift = np.roll(img_array, -1, axis=0)
    down_shift = np.roll(img_array, 1, axis=0)
    left_shift = np.roll(img_array, -1, axis=1)
    right_shift = np.roll(img_array, 1, axis=1)
    
    # 找到邊界像素點
    boundary_mask = ((img_array > 0) & 
                     ((up_shift == 0) | (down_shift == 0) | (left_shift == 0) | (right_shift == 0)))
    
    # 將邊界點設置為指定顏色
    boundary_img_array[boundary_mask] = color
    
    # 將NumPy陣列轉換為PIL圖像並返回
    boundary_img = Image.fromarray(boundary_img_array)
    
    return boundary_img



# def mark_boundary_points(input_image_path, output_folder, color=(255, 0, 0)):
#     # 打開圖像
#     img = Image.open(input_image_path)
    
#     # 確保圖像是8位元深度的灰階圖像
#     if img.mode != 'L':
#         img = img.convert('L')
    
#     # 創建一個新圖像來標記邊界點，初始化為黑色
#     boundary_img = Image.new('RGB', img.size, (0, 0, 0))
#     img = img.point(lambda p: p if p >= 10 else 0)
    
#     # 獲取圖像的寬度和高度
#     width, height = img.size
    
#     # 迭代圖像的每個像素
#     for y in range(height):
#         for x in range(width):
#             pixel_value = img.getpixel((x, y))
            
#             # 檢查是否是黑色像素
#             if pixel_value > 0:
#                 # 檢查上一個點是否小於255
#                 if y > 0 and img.getpixel((x, y - 1)) == 0:
#                     boundary_img.putpixel((x, y), color)  # 使用指定顏色標記
                
#                 # 檢查下一個點是否小於255
#                 if y < height - 1 and img.getpixel((x, y + 1)) == 0:
#                     boundary_img.putpixel((x, y), color)  # 使用指定顏色標記
                
#                 # 檢查左邊的點是否小於255
#                 if x > 0 and img.getpixel((x - 1, y)) == 0:
#                     boundary_img.putpixel((x, y), color)  # 使用指定顏色標記
                
#                 # 檢查右邊的點是否小於255
#                 if x < width - 1 and img.getpixel((x + 1, y)) == 0:
#                     boundary_img.putpixel((x, y), color)  # 使用指定顏色標記
    
#     # 建立輸出的檔名，保存到相同的資料夾下
#     output_image_path = os.path.join(output_folder, os.path.basename(input_image_path))
#     boundary_img.save(output_image_path)

# # 設定輸出資料夾
# output_folder_prep = os.path.join(base_folder, output_folder_base_prep)
# output_folder_op = os.path.join(base_folder, output_folder_base_op)

# # 如果輸出資料夾不存在，則創建它們
# if not os.path.exists(output_folder_prep):
#     os.makedirs(output_folder_prep)

# if not os.path.exists(output_folder_op):
#     os.makedirs(output_folder_op)

# # 遍歷所有指定的資料夾

# for folder_name in input_folders:
#     folder_path = os.path.join(base_folder, folder_name, "Up")

#     # 處理當前資料夾中的圖像
#     image_files = os.listdir(folder_path)
#     for image_file in image_files:
#         if image_file.endswith(".png"):
#             input_image_path = os.path.join(folder_path, image_file)
#             mark_boundary_points(input_image_path, output_folder_op, color=(255, 255, 0)) 


# for folder_name in input_folders:
#     folder_path = os.path.join(base_folder, folder_name, "Down")

#     # 處理當前資料夾中的圖像
#     image_files = os.listdir(folder_path)
#     for image_file in image_files:
#         if image_file.endswith(".png"):
#             input_image_path = os.path.join(folder_path, image_file)
#             mark_boundary_points(input_image_path, output_folder_prep)
