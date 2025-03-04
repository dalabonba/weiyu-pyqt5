
import numpy as np
from skimage.metrics import structural_similarity as mssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import os
import torch
# import matplotlib.pyplot as plt
import cv2
from .fsim import FSIM, FSIMc
# import Niqe
from sklearn.metrics import mean_squared_error
from .forSSIM.crop import crop_to_mask
# from colormath.color_objects import LabColor
# from colormath.color_diff import delta_e_cie1976
def cal_ssim_psnr(img1,img2):#一次性读一个文件夹

    cal_psnr=[]
    cal_ssim=[]

    cal_psnr.append(psnr(img1, img2))
    cal_ssim.append(mssim(img1, img2, multichannel=True, win_size=None))
    return np.array(cal_psnr).mean(),np.array(cal_ssim).mean()

def cal_fsim(img1,img2):#一次性读一个文件夹

    cal_fsim = []
    # Size of the batch for training
    batch_size = 1

    # Read reference and distorted images
    img1 = torch.from_numpy(np.asarray(img1))
    img1 = img1.permute(2, 0, 1)
    img1 = img1.unsqueeze(0).type(torch.FloatTensor)
    img2 = torch.from_numpy(np.asarray(img2))
    img2 = img2.permute(2, 0, 1)
    img2 = img2.unsqueeze(0).type(torch.FloatTensor)

    # Create fake batch (for testing)
    img1b = torch.cat(batch_size * [img1], 0)
    img2b = torch.cat(batch_size * [img2], 0)

    if torch.cuda.is_available():
        img1b = img1b.cuda()
        img2b = img2b.cuda()

    # Create FSIM loss
    FSIM_loss = FSIM()
    loss = FSIM_loss(img1b, img2b)
    cal_fsim.append(loss.cpu().detach().numpy())
    return np.array(cal_fsim).mean()

# def cal_niqe(path1,path2):#一次性读一个文件夹
#     img_low = os.listdir(path1)
#     img_high = os.listdir(path2)

#     cal_niqe = []
#     for i in range(15):
#         ref = np.array(Image.open(path1 +'/'+ img_low[i]).convert('LA'))[:,:,0] # ref
#         cal_niqe.append(Niqe.niqe(ref))
#     return np.array(cal_niqe).mean()

# def cal_lpips(path1,path2):#一次性读一个文件夹
#     img_low = os.listdir(path1)
#     img_high = os.listdir(path2)
    
#     use_gpu = True         # Whether to use GPU
#     spatial = True 
#     cal_lpips = []
#     for i in range(15):
#         loss_fn = lpips.LPIPS(net='alex', spatial=spatial)
#         if(use_gpu):
# 	        loss_fn.cuda()
#         dummy_img0 = lpips.im2tensor(lpips.load_image(path1 +'/'+ img_low[i]))
#         dummy_img1 = lpips.im2tensor(lpips.load_image(path2 +'/'+ img_low[i]))
#         dummy_img0 = dummy_img0.cuda()
#         dummy_img1 = dummy_img1.cuda()
#         dist = loss_fn.forward(dummy_img0, dummy_img1)
#         cal_lpips.append(dist.mean().item())
#     return np.array(cal_lpips).mean()

def cal_rmse(img1,img2):#一次性读一个文件夹

    cal_rmse = []
    img1_flat = img1.reshape(-1, 3)
    img2_flat = img2.reshape(-1, 3)
    # print(img1)
    rms = mean_squared_error(img1_flat, img2_flat, squared=False)
    cal_rmse.append(rms)
    return np.array(cal_rmse).mean()

# def cal_deltae(path1,path2):#一次性读一个文件夹
#     img_low = os.listdir(path1)
#     img_high = os.listdir(path2)
#     cal_deltae = []
#     for i in range(15):
#         deltae = skimage.color.deltaE_cie76(path1 +'/'+ img_low[i], path1 +'/'+ img_high[i])
#         cal_deltae.append(deltae)
#     return np.array(cal_deltae).mean()

# def pi(path1,path2):
#     img_low = os.listdir(path1)
#     img_high = os.listdir(path2)
#     cal_pi = []
#     for i in range(15):
        
#         cal_pi.append(pi)
#     return np.array(cal_pi).mean()

def cal_all(path_high, path, txt_path, mask_path=None):
    print('computing...')
    file = open(txt_path, 'w', encoding='utf-8')
    file_list = os.listdir(path)
    c_psnr = []
    c_ssim = []
    c_fsim = []
    c_rmse = []

    # 保存原始的ground truth路徑
    original_path_high = path_high
    
    for i in file_list:
        # 使用原始路徑來構建新的路徑
        gt_image_path = os.path.join(original_path_high, i)  # ground truth圖片的路徑
        test_image_path = os.path.join(path, i)             # 測試圖片的路徑

        # print(f"Ground truth path: {gt_image_path}")
        # print(f"Test image path: {test_image_path}")
        # print(f"Processing {i}")
        
        # 如果提供了遮罩，則進行裁剪
        if mask_path:
            mask_file = os.path.join(mask_path, i.replace(".jpg", ".png"))  # 假設遮罩與圖片檔案名相同，只是副檔名不同
            if os.path.exists(mask_file):
                cropped_gt, marked_gt = crop_to_mask(gt_image_path, mask_file)
                cropped_test, marked_test = crop_to_mask(test_image_path, mask_file)
            else:
                print()
                continue
        else:
            cropped_gt = cv2.imread(gt_image_path)
            cropped_test = cv2.imread(test_image_path)

        # 計算指標
        a, b = cal_ssim_psnr(cropped_test, cropped_gt)
        c = cal_fsim(cropped_test, cropped_gt)
        f = cal_rmse(cropped_test, cropped_gt)
            
        c_psnr.append(a)
        c_ssim.append(b)
        c_fsim.append(c)
        c_rmse.append(f)
            
        # 寫入結果
        result_str = (f"{i} - PSNR: {a:.4f}, SSIM: {b:.4f}, "
                        f"FSIM: {c:.4f}, RMSE: {f:.4f}\n")
        file.write(result_str)
        print(result_str)

    if len(c_psnr) > 0:  # 確保有成功處理的數據
        # 計算平均值
        avg_psnr = np.mean(c_psnr)
        avg_ssim = np.mean(c_ssim)
        avg_fsim = np.mean(c_fsim)
        avg_rmse = np.mean(c_rmse)
        
        # 寫入平均值
        avg_str = (f"\nAverages:\nPSNR: {avg_psnr:.4f}\nMS-SSIM: {avg_ssim:.4f}\n"
                   f"FSIM: {avg_fsim:.4f}\nRMSE: {avg_rmse:.4f}")
        file.write(avg_str)
        print(avg_str)
    
    file.close()
    print('Computation completed')




# gtPath = "D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/prdeictdata/Differentdepth_answer/r=2.5/" # 正解資料集路徑
# resultPath = "D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/prdeictdata/forprdeictDAIS/r=2.5/" # 修復結果資料夾路徑
# txtPath = "D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/fortestmask/Different_depth_DAIS/r=2.5.txt" # 遮罩資料夾路徑
# maskPath = "D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/fortestmask/DAIS/"
# # Example usage:
# cal_all(gtPath,resultPath,txtPath,maskPath)#文件放这


