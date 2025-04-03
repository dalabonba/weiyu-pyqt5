import numpy as np
from skimage.metrics import structural_similarity as mssim  # 結構相似性指標 (SSIM)
from skimage.metrics import peak_signal_noise_ratio as psnr  # 峰值信噪比 (PSNR)
import os
import torch
# import matplotlib.pyplot as plt  # 繪圖庫（已註解）
import cv2  # OpenCV 用於圖像處理
from .fsim import FSIM, FSIMc  # 自定義 FSIM 模組（特徵相似性指標）
# import Niqe  # NIQE 模組（已註解）
from sklearn.metrics import mean_squared_error  # 均方根誤差 (RMSE)
from .forSSIM.crop import crop_to_mask  # 自定義裁剪模組

# 計算 SSIM 和 PSNR
def cal_ssim_psnr(img1, img2):
    """
    計算兩張圖像的 PSNR 和 SSIM。
    參數:
        img1: 第一張圖像 (修復圖像)
        img2: 第二張圖像 (真實圖像)
    返回:
        PSNR 和 SSIM 的平均值
    """
    cal_psnr = []
    cal_ssim = []

    cal_psnr.append(psnr(img1, img2))  # 計算並添加 PSNR 值
    cal_ssim.append(mssim(img1, img2, multichannel=True, win_size=None))  # 計算並添加 SSIM 值，多通道模式
    return np.array(cal_psnr).mean(), np.array(cal_ssim).mean()  # 返回平均值

# 計算 FSIM（特徵相似性指標）
def cal_fsim(img1, img2):
    """
    計算兩張圖像的 FSIM。
    參數:
        img1: 第一張圖像 (修復圖像)
        img2: 第二張圖像 (真實圖像)
    返回:
        FSIM 的平均值
    """
    cal_fsim = []
    batch_size = 1  # 批次大小設為 1

    # 將圖像轉換為 PyTorch 張量並調整維度
    img1 = torch.from_numpy(np.asarray(img1))  # 轉換為 NumPy 陣列後再轉為張量
    img1 = img1.permute(2, 0, 1)  # 調整維度為 (通道, 高度, 寬度)
    img1 = img1.unsqueeze(0).type(torch.FloatTensor)  # 添加批次維度並轉為浮點型
    img2 = torch.from_numpy(np.asarray(img2))
    img2 = img2.permute(2, 0, 1)
    img2 = img2.unsqueeze(0).type(torch.FloatTensor)

    # 創建假批次（測試用）
    img1b = torch.cat(batch_size * [img1], 0)
    img2b = torch.cat(batch_size * [img2], 0)

    # 如果有 GPU 可用，則將數據移至 GPU
    if torch.cuda.is_available():
        img1b = img1b.cuda()
        img2b = img2b.cuda()

    # 創建 FSIM 損失函數並計算
    FSIM_loss = FSIM()
    loss = FSIM_loss(img1b, img2b)
    cal_fsim.append(loss.cpu().detach().numpy())  # 將結果轉回 CPU 並添加到列表
    return np.array(cal_fsim).mean()  # 返回平均值

# 計算 RMSE（均方根誤差）
def cal_rmse(img1, img2):
    """
    計算兩張圖像的 RMSE。
    參數:
        img1: 第一張圖像 (修復圖像)
        img2: 第二張圖像 (真實圖像)
    返回:
        RMSE 的平均值
    """
    cal_rmse = []
    img1_flat = img1.reshape(-1, 3)  # 將圖像展平為一維陣列（每個像素有3個通道）
    img2_flat = img2.reshape(-1, 3)
    rms = mean_squared_error(img1_flat, img2_flat, squared=False)  # 計算 RMSE
    cal_rmse.append(rms)
    return np.array(cal_rmse).mean()  # 返回平均值

# 計算所有指標並保存結果
def cal_all(path_high, path, txt_path, mask_path=None):
    """
    計算指定資料夾中所有圖像的 PSNR、SSIM、FSIM 和 RMSE，並將結果保存到文本文件。
    參數:
        path_high: 真實圖像資料夾路徑
        path: 修復圖像資料夾路徑
        txt_path: 結果保存的文本文件路徑
        mask_path: 遮罩圖像資料夾路徑（可選）
    """
    print('computing...')  # 提示計算開始
    file = open(txt_path, 'w', encoding='utf-8')  # 打開文本文件以寫入結果
    file_list = os.listdir(path)  # 獲取修復圖像資料夾中的文件列表
    c_psnr = []
    c_ssim = []
    c_fsim = []
    c_rmse = []

    # 保存原始的真實圖像路徑
    original_path_high = path_high
    
    # 遍歷修復圖像文件
    for i in file_list:
        gt_image_path = os.path.join(original_path_high, i)  # 構建真實圖像路徑
        test_image_path = os.path.join(path, i)  # 構建修復圖像路徑
        
        # 如果提供了遮罩路徑，則根據遮罩裁剪圖像
        if mask_path:
            mask_file = os.path.join(mask_path, i.replace(".jpg", ".png"))  # 假設遮罩文件為PNG格式
            if os.path.exists(mask_file):
                cropped_gt, marked_gt = crop_to_mask(gt_image_path, mask_file)  # 裁剪真實圖像
                cropped_test, marked_test = crop_to_mask(test_image_path, mask_file)  # 裁剪修復圖像
            else:
                print()  # 如果遮罩文件不存在，打印空行並跳過
                continue
        else:
            # 如果沒有遮罩，直接讀取圖像
            cropped_gt = cv2.imread(gt_image_path)
            cropped_test = cv2.imread(test_image_path)

        # 計算各項指標
        a, b = cal_ssim_psnr(cropped_test, cropped_gt)  # PSNR 和 SSIM
        c = cal_fsim(cropped_test, cropped_gt)  # FSIM
        f = cal_rmse(cropped_test, cropped_gt)  # RMSE
            
        # 將結果添加到列表
        c_psnr.append(a)
        c_ssim.append(b)
        c_fsim.append(c)
        c_rmse.append(f)
            
        # 格式化並寫入單張圖像的結果
        result_str = (f"{i} - PSNR: {a:.4f}, SSIM: {b:.4f}, "
                      f"FSIM: {c:.4f}, RMSE: {f:.4f}\n")
        file.write(result_str)
        print(result_str)  # 同時打印到控制台

    # 如果有成功處理的數據，計算並保存平均值
    if len(c_psnr) > 0:
        avg_psnr = np.mean(c_psnr)  # 平均 PSNR
        avg_ssim = np.mean(c_ssim)  # 平均 SSIM
        avg_fsim = np.mean(c_fsim)  # 平均 FSIM
        avg_rmse = np.mean(c_rmse)  # 平均 RMSE
        
        # 格式化並寫入平均值
        avg_str = (f"\nAverages:\nPSNR: {avg_psnr:.4f}\nMS-SSIM: {avg_ssim:.4f}\n"
                   f"FSIM: {avg_fsim:.4f}\nRMSE: {avg_rmse:.4f}")
        file.write(avg_str)
        print(avg_str)
    
    file.close()  # 關閉文件
    print('Computation completed')  # 提示計算完成