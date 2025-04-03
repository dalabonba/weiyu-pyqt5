from PyQt5.QtCore import pyqtSignal
import os
from .BaseModel import BaseModel
from Otherfunction import readmodel, trianglegood

class RemeshModel(BaseModel):
    model_updated = pyqtSignal()  # 定義類級別的信號，用於通知模型更新

    # 初始化函數
    def __init__(self):
        super().__init__()  # 調用父類的構造函數
        self.image_file = ""  # 2D圖片文件路徑
        self.reference_file = ""  # 3D參考模型文件路徑
        self.output_folder = ""  # 輸出文件夾路徑

    # 設置3D參考文件
    def set_reference_file(self, file_path):
        if os.path.exists(file_path):  # 檢查文件是否存在
            self.reference_file = file_path  # 設置參考文件路徑
            self.model_updated.emit()  # 發送信號通知模型已更新
            return True
        return False

    # 設置2D圖片文件
    def set_image_file(self, file_path):
        if os.path.exists(file_path):  # 檢查文件是否存在
            self.image_file = file_path  # 設置圖片文件路徑
            self.model_updated.emit()  # 發送信號通知模型已更新
            return True
        return False

    # 保存3D重建結果
    def save_remesh_file(self, renderer, render2):
        # 檢查是否所有必要文件和路徑都已設置
        if self.image_file and self.output_folder and self.reference_file:
            # 清理圖片文件路徑中的多餘引號和空格
            image_file_cleaned = self.image_file.strip("' ").strip()
            # 提取文件名（不含擴展名）
            base_name = os.path.splitext(os.path.basename(image_file_cleaned))[0]
            # 定義輸出STL文件路徑
            output_stl_path = self.output_folder + '/' + base_name + ".stl"
            # 使用DentalModelReconstructor進行3D重建
            trianglegood.DentalModelReconstructor(self.image_file, self.reference_file, output_stl_path).reconstruct()
            # 在第二個渲染窗口中顯示重建結果
            readmodel.render_file_in_second_window(render2, output_stl_path)
        return True  # 返回True表示操作完成（即使條件不滿足也返回True，可能需要改進邏輯）