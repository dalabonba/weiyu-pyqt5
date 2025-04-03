from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from .baseview import BaseView  

class AnalysisView(BaseView):
    # 初始化函數，設置視圖的基本屬性
    def __init__(self, parent_layout, model, renderinput, renderinput2):
        super().__init__(parent_layout, renderinput, renderinput2)  # 調用父類的初始化函數
        self.model = model  # 儲存模型對象

    # 創建遮罩贋復區域分析面板
    def create_edge(self, parent_layout, current_panel):
        # 如果當前面板存在，則移除
        if current_panel:
            parent_layout.removeWidget(current_panel)

        # 創建帶標題的組框，標題為"遮罩贋復區域分析"
        panel = QGroupBox("遮罩贋復區域分析")
        layout = QVBoxLayout()  # 創建垂直佈局

        # 真實圖檔資料夾選擇
        self.groudtruth_file = QLineEdit()  # 創建真實圖檔輸入框
        self.create_file_selection_layout(layout, "真實圖檔資料夾:", self.groudtruth_file,
                                          self.model.set_groudtruth_folder)  # 使用父類方法創建文件選擇佈局

        # 修復圖檔資料夾選擇
        self.result_file = QLineEdit()  # 創建修復圖檔輸入框
        self.create_file_selection_layout(layout, "修復圖檔資料夾:", self.result_file,
                                          self.model.set_result_folder)  # 使用父類方法創建文件選擇佈局
        
        # 遮罩圖檔資料夾選擇
        self.mask_file = QLineEdit()  # 創建遮罩圖檔輸入框
        self.create_file_selection_layout(layout, "遮罩圖檔資料夾:", self.mask_file,
                                          self.model.set_mask_folder)  # 使用父類方法創建文件選擇佈局

        # 輸出文件夾選擇
        self.output_layout = QHBoxLayout()  # 創建水平佈局（未使用，可能是遺留代碼）
        self.output_folder = QLineEdit()  # 創建輸出文件夾輸入框
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder,
                                          self.model.set_output_folder)  # 使用父類方法創建文件選擇佈局

        # 創建並設置保存按鈕
        save_button = QPushButton("保存分析數值")
        save_button.clicked.connect(self.save_value_file)  # 綁定點擊事件到保存函數
        layout.addWidget(save_button)  # 添加按鈕到佈局

        panel.setLayout(layout)  # 設置面板的佈局
        parent_layout.addWidget(panel)  # 添加面板到父佈局
        return panel  # 返回創建的面板

    # 更新視圖內容
    def update_view(self):
        # 根據模型的當前狀態更新視圖
        self.groudtruth_file.setText(self.model.groudtruth_file)  # 更新真實圖檔路徑顯示
        self.result_file.setText(self.model.result_file)  # 更新修復圖檔路徑顯示
        self.mask_file.setText(self.model.mask_file)  # 更新遮罩圖檔路徑顯示
        self.output_folder.setText(self.model.output_folder)  # 更新輸出文件夾路徑顯示

    # 保存分析數值
    def save_value_file(self):
        # 調用模型的保存方法並檢查結果
        if self.model.save_value_button(self.render_input, self.render_input2):
            print("Depth map saved successfully")  # 成功保存深度圖（這裡的訊息可能需要調整為更符合分析數值的描述）
        else:
            print("Failed to save depth map")  # 保存失敗（同上）