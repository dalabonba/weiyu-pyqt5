from PIL import Image  # 用於圖像處理的 PIL 庫
import os  # 用於文件和目錄操作
import argparse  # 用於解析命令行參數

# 命令行參數設置
parser = argparse.ArgumentParser()  # 創建參數解析器
parser.add_argument("--input_dir", default="D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/foranswer/", 
                    help="輸入 PNG 圖像文件夾")  # 定義輸入文件夾參數
parser.add_argument("--output_dir", default="D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/foranswercrop/", 
                    help="輸出 PNG 圖像文件夾")  # 定義輸出文件夾參數
args = parser.parse_args()  # 解析命令行參數

def crop_and_resize_image(input_file, output_file, scale_size=730, crop_size=256):
    """
    裁剪並調整圖片大小，保存到指定位置。
    參數:
        input_file: 輸入圖片文件路徑
        output_file: 輸出圖片文件路徑
        scale_size: 縮放到的尺寸（預設為730）
        crop_size: 裁剪區域的大小（預設為256）
    """
    img = Image.open(input_file)  # 打開輸入圖像文件

    # 計算偏移量（根據縮放比例調整）
    offset_height = int(95 * (scale_size / crop_size))  # 高度偏移量
    offset_width = int(80 * (scale_size / crop_size))   # 寬度偏移量

    # 調整圖片大小至 [scale_size, scale_size]，使用抗鋸齒濾波
    img = img.resize((scale_size, scale_size), Image.ANTIALIAS)

    # 設置裁剪區域 (left, upper, right, lower)
    left = offset_width  # 左邊界
    top = offset_height  # 上邊界
    right = offset_width + crop_size  # 右邊界
    bottom = offset_height + crop_size  # 下邊界

    # 裁剪圖片
    img = img.crop((left, top, right, bottom))

    # 保存裁剪後的圖片為 PNG 格式
    img.save(output_file, format="PNG")

def process_folder(input_dir, output_dir, scale_size=730, crop_size=256):
    """
    遍歷文件夾，裁剪並保存圖片。
    參數:
        input_dir: 輸入文件夾路徑
        output_dir: 輸出文件夾路徑
        scale_size: 縮放到的尺寸（預設為730）
        crop_size: 裁剪區域的大小（預設為256）
    """
    # 如果輸出文件夾不存在，則創建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍歷輸入文件夾中的所有文件
    for filename in os.listdir(input_dir):
        input_file = os.path.join(input_dir, filename)  # 構建輸入文件完整路徑
        output_file = os.path.join(output_dir, filename)  # 構建輸出文件完整路徑

        # 檢查是否為文件且為 PNG 格式
        if os.path.isfile(input_file) and input_file.lower().endswith('.png'):
            print(f"Processing file: {input_file}")  # 打印正在處理的文件
            crop_and_resize_image(input_file, output_file, scale_size, crop_size)  # 裁剪並調整圖片
            print(f"Saved to: {output_file}")  # 打印保存位置

if __name__ == "__main__":
    # 從命令行參數獲取輸入和輸出文件夾路徑
    input_dir = args.input_dir
    output_dir = args.output_dir

    # 執行文件夾處理
    process_folder(input_dir, output_dir)