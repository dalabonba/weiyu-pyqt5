import tensorflow as tf
import matplotlib.pyplot as plt
import os
tf.compat.v1.enable_eager_execution()

# 使用 TensorFlow 讀取圖片並轉換為灰階
image_path = './combinetwoedge/data0402_his.png'  # 修改為你的圖片路徑
image = tf.io.read_file(image_path)
image = tf.image.decode_image(image, channels=1)  # 讀取為灰階
image = tf.cast(image, tf.float32)  # 將數據轉換為 float32
# ✅ 將 0 以外的像素過濾掉
nonzero_image = tf.boolean_mask(image, image > 0)


# ✅ 使用非零像素計算直方圖 (256 區間)
histogram = tf.histogram_fixed_width(nonzero_image, [0.0, 255.0], nbins=256).numpy()

# ✅ 可視化非零像素分佈
plt.figure(figsize=(10, 6))
plt.bar(range(256), histogram, color='gray')
plt.title('Histogram hfake  historgram')
plt.xlabel('occlusal gap distance(mm)')
plt.ylabel('Frequency')

# ✅ 將 x 軸範圍限制在非零像素，並縮小範圍
plt.xlim(1, 255)
plt.xticks([0, 51, 102, 153, 204, 255, 306], labels=['0.0', '1.0', '2.0', '3.0', '4.0', '5.0','6.0'])
os.makedirs('figure', exist_ok=True)
save_path = os.path.join('figure', os.path.splitext(os.path.basename(image_path))[0] + '.png')
plt.savefig(save_path)
plt.show()


