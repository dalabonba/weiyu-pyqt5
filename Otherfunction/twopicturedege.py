import numpy as np
from PIL import Image
import os
import numba
from .imageProcess import calculate_image_difference
from .getimage import apply_blue_mask
# import vtk
# red_folder_path = "D:/Users/user/Desktop/papergan/paper/crown/traincode/test/Prepedgered"
# yellow_output_folder = "D:/Users/user/Desktop/papergan/paper/crown/traincode/test/Prepedgeyellow"
# output_folder = "D:/Users/user/Desktop/papergan/paper/crown/traincode/combineedge/"



@numba.jit(nopython=True)
def process_image(img_array, img1_array):
    height, width = img_array.shape[:2]
    result = np.zeros_like(img_array)

    
    for y in range(height):
        red_start_x = yellow_start_x = red_end_x = yellow_end_x = 0
        start_red_x_set = start_yellow_x_set = False
        
        for x in range(width):
            pixel_img = img_array[y, x]
            pixel_img1 = img1_array[y, x]
            
            is_red_or_green = np.any(pixel_img1 != 0) or np.all(pixel_img1 == np.array([0, 255, 0]))
            is_yellow_or_green = np.any(pixel_img != 0) or np.all(pixel_img == np.array([0, 255, 0]))
            
            if is_red_or_green:
                if not start_red_x_set:
                    red_start_x = x
                red_end_x = x
                start_red_x_set = True
            
            if is_yellow_or_green:
                if not start_yellow_x_set:
                    yellow_start_x = x
                yellow_end_x = x
                start_yellow_x_set = True
        
        start_x = max(red_start_x, yellow_start_x)
        end_x = min(red_end_x, yellow_end_x)
        
        if end_x > start_x:
            result[y, start_x:end_x+1] = np.array([255, 0, 0])  # Blue bgr
    
    return result
def ensure_png_extension(file_path):
    return file_path if file_path.lower().endswith(".png") else file_path + ".png"


def combine_image(input_image_path, input2_image_path, output_folder,downimage,upimage):
    input_image_path = ensure_png_extension(input_image_path)
    input2_image_path = ensure_png_extension(input2_image_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_image_path = os.path.join(output_folder, os.path.basename(input_image_path))
    img = Image.open(input_image_path).convert('RGB')
    img1 = Image.open(input2_image_path).convert('RGB')
    img_array = np.array(img)
    img1_array = np.array(img1)
    # Process the image
    blue_result_array = process_image(img_array, img1_array)
    # cv2.imwrite(output_image_path, blue_result_array)
    get_combine_data = calculate_image_difference(upimage,downimage)
    combine_image_array_np = np.array(get_combine_data)
    blue_image_array_np = np.array(blue_result_array)
    
    # Save the result
    apply_blue_mask(combine_image_array_np,blue_image_array_np,output_image_path)



# def combine_image(input_image_path, input2_image_path, output_folder):
#     # 确保输出文件夹存在
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
#     # 打开图像
#     img = Image.open(input_image_path)
#     img1 = Image.open(input2_image_path)

#     # 确保图像是24位的彩色图像
#     if img.mode != 'RGB':
#         img = img.convert('RGB')
#     if img1.mode != 'RGB':
#         img1 = img1.convert('RGB')

#     # 将图像转换为 numpy 数组
#     img_array = np.array(img)
#     img1_array = np.array(img1)

#     # 创建一个新图像来标记边界点，初始化为黑色
#     boundary_img_array = np.zeros_like(img_array)

#     # 条件：img1的像素不是黑色
#     red_condition = (img1_array[:, :, 0] != 0) | (img1_array[:, :, 1] != 0) | (img1_array[:, :, 2] != 0)
    
#     # 条件：img的像素不是黑色
#     yellow_condition = (img_array[:, :, 0] != 0) | (img_array[:, :, 1] != 0) | (img_array[:, :, 2] != 0)

#     # 标记为黄色（255, 255, 0）: 满足 red_condition 的像素
#     boundary_img_array[red_condition] = [255, 255, 0]

#     # 标记为红色（255, 0, 0）: 满足 yellow_condition 且 boundary_img_array 还没有标记的像素
#     boundary_img_array[yellow_condition & ~red_condition] = [255, 0, 0]

#     # 标记为绿色（0, 255, 0）: 满足 yellow_condition 且已经标记为黄色的像素
#     boundary_img_array[yellow_condition & red_condition] = [0, 255, 0]

#     # 将结果保存为图像
#     boundary_img = Image.fromarray(boundary_img_array)
    


#     # 保存结果图像
#     output_image_path = os.path.join(output_folder, os.path.basename(input_image_path))
#     boundary_img.save(output_image_path)

#     blue = [0, 0, 255]
#     yellow = [100, 100, 0]
#     red = [2, 0, 0]
#     green = [0, 255, 0]
#     reader = vtk.vtkPNGReader()
#     reader.SetFileName(output_image_path)
#     reader.Update()

#     image = reader.GetOutput()
#     dimensions = image.GetDimensions()


#     for y in range(dimensions[1]):
#         red_start_x = yellow_start_x = red_end_x = yellow_end_x = start_x = end_x = 0
#         start_red_x_set = start_yellow_x_set = False

#         for x in range(dimensions[0]):
#             pixel = get_pixel(image, x, y)
            
#             # 檢查紅色或綠色像素
#             if (pixel[0] != 0 and pixel[1] == red[1] and pixel[2] == red[2]) or \
#                 (pixel[0] == green[0] and pixel[1] == green[1] and pixel[2] == green[2]):
#                 if not start_red_x_set:
#                     red_start_x = x
#                 red_end_x = x
#                 start_red_x_set = True

#             # 檢查黃色或綠色像素
#             if (pixel[0] != 0 and pixel[1] != 0 and pixel[2] == yellow[2]) or \
#                 (pixel[0] == green[0] and pixel[1] == green[1] and pixel[2] == green[2]):
#                 if not start_yellow_x_set:
#                     yellow_start_x = x
#                 yellow_end_x = x
#                 start_yellow_x_set = True

#         # 決定起始和結束點
#         start_x = max(red_start_x, yellow_start_x)
#         end_x = min(red_end_x, yellow_end_x)

#         # 將起點到終點之間的像素塗成藍色
#         if end_x > start_x:
#             for x in range(start_x, end_x + 1):
#                 set_pixel(image, x, y, blue)

#     # 移除黃色、紅色和綠色像素
#     for y in range(dimensions[1]):
#         for x in range(dimensions[0]):
#             pixel = get_pixel(image, x, y)
#             if (pixel[0] != 0 and pixel[1] != 0 and pixel[2] == 0) or \
#                 (pixel[0] != 0 and pixel[1] == 0 and pixel[2] == 0) or \
#                 (pixel[0] == 0 and pixel[1] != 0 and pixel[2] == 0):
#                     set_pixel(image, x, y, [0, 0, 0])

#     # 保存處理後的圖像
#     writer = vtk.vtkPNGWriter()
#     writer.SetFileName(output_image_path)
#     writer.SetInputData(image)
#     writer.Write()


# # 函數來獲取像素值
# def get_pixel(image, x, y):
#     return [int(image.GetScalarComponentAsDouble(x, y, 0, i)) for i in range(3)]

# # 函數來設置像素值
# def set_pixel(image, x, y, color):
#     for i in range(3):
#         image.SetScalarComponentFromDouble(x, y, 0, i, color[i])
# red_image_files = os.listdir(red_folder_path)


# for image_file in red_image_files:
#     if image_file.endswith(".png"):  # 假設圖像檔案是PNG格式
#         input_image_path = os.path.join(red_folder_path, image_file)
#         input2_image_path = os.path.join(yellow_output_folder, image_file)
#         output_image_path = os.path.join(output_folder, image_file)
#         combine_image(input_image_path, input2_image_path, output_image_path)
