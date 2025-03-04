from PIL import Image
import os
import argparse

# 命令行參數
parser = argparse.ArgumentParser()
parser.add_argument("--input_dir",default="D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/foranswer/", help="输入 PNG 图像文件夹")
parser.add_argument("--output_dir",default="D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/foranswercrop/", help="输出 PNG 图像文件夹")
args = parser.parse_args()

def crop_and_resize_image(input_file, output_file, scale_size=730, crop_size=256):
    """
    裁剪并调整图片大小，保存到指定位置。
    :param input_file: 输入图片文件路径
    :param output_file: 输出图片文件路径
    :param scale_size: 缩放到的尺寸
    :param crop_size: 裁剪区域的大小
    """
    img = Image.open(input_file)

    # 计算偏移
    offset_height = int(95 * (scale_size / crop_size))  # 高度偏移
    offset_width = int(80 * (scale_size / crop_size))  # 宽度偏移

    # 调整图片大小至 [scale_size, scale_size]
    img = img.resize((scale_size, scale_size), Image.ANTIALIAS)

    # 设置裁剪区域 (left, upper, right, lower)
    left = offset_width
    top = offset_height
    right = offset_width + crop_size
    bottom = offset_height + crop_size

    # 裁剪图片
    img = img.crop((left, top, right, bottom))

    # 保存图片
    img.save(output_file, format="PNG")

def process_folder(input_dir, output_dir, scale_size=730, crop_size=256):
    """
    遍历文件夹，裁剪并保存图片。
    :param input_dir: 输入文件夹路径
    :param output_dir: 输出文件夹路径
    :param scale_size: 缩放到的尺寸
    :param crop_size: 裁剪区域的大小
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, filename)

        if os.path.isfile(input_file) and input_file.lower().endswith('.png'):
            print(f"Processing file: {input_file}")
            crop_and_resize_image(input_file, output_file, scale_size, crop_size)
            print(f"Saved to: {output_file}")

if __name__ == "__main__":
    input_dir = args.input_dir
    output_dir = args.output_dir

    process_folder(input_dir, output_dir)
