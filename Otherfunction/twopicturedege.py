from PIL import Image
import os

red_folder_path = "D:/Users/user/Desktop/papergan/paper/crown/traincode/test/Prepedgered"
yellow_output_folder = "D:/Users/user/Desktop/papergan/paper/crown/traincode/test/Prepedgeyellow"
output_folder = "D:/Users/user/Desktop/papergan/paper/crown/traincode/combineedge/"

def mark_boundary_points(input_image_path, input2_image_path, output_folder):
    # 打開圖像
    img = Image.open(input_image_path)
    img1 = Image.open(input2_image_path)

    # 確保圖像是24位元的彩色圖像
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 創建一個新圖像來標記邊界點，初始化為黑色
    boundary_img = Image.new('RGB', img.size, (0, 0, 0))

    # 獲取圖像的寬度和高度
    width, height = img.size

    # 迭代圖像的每個像素
    for y in range(height):
        for x in range(width):
            pixel_value = img.getpixel((x, y))
            pixel_value1 = img1.getpixel((x, y))

            # 檢查紅色通道是否大於1
            if pixel_value1[0] != 0 or pixel_value1[1] != 0 or pixel_value1[2] != 0:
                # 標記為紅色
                boundary_img.putpixel((x, y), (255, 255, 0))
            # 檢查黃色通道是否大於1
            if pixel_value[0] != 0 or pixel_value[1] != 0 or pixel_value[2] != 0:
                # 如果該像素已經被標記為紅色，標記為綠色；否則，標記為黃色
                if boundary_img.getpixel((x, y)) == (255, 255, 0):
                    boundary_img.putpixel((x, y), (0, 255, 0))
                else:
                    boundary_img.putpixel((x, y), (255, 0, 0))

    boundary_img.save(output_folder)

red_image_files = os.listdir(red_folder_path)
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for image_file in red_image_files:
    if image_file.endswith(".png"):  # 假設圖像檔案是PNG格式
        input_image_path = os.path.join(red_folder_path, image_file)
        input2_image_path = os.path.join(yellow_output_folder, image_file)
        output_image_path = os.path.join(output_folder, image_file)
        mark_boundary_points(input_image_path, input2_image_path, output_image_path)
