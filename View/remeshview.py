# singledepthview.py
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import Qt
from .baseview import BaseView  
from Otherfunction import readmodel

class RemeshView(BaseView):
    # 初始化函數，設置視圖的基本屬性
    def __init__(self, parent_layout, model, renderinput, renderinput2):
        super().__init__(parent_layout, renderinput, renderinput2)  # 調用父類的初始化函數
        self.model = model  # 儲存模型對象
        model.model_updated.connect(self.update_view)  # 當模型更新時觸發視圖更新

    # 創建3D重建面板
    def create_remesh(self, parent_layout, current_panel):
        # 如果當前面板存在，則移除
        if current_panel:
            parent_layout.removeWidget(current_panel)

        # 創建帶標題的組框，標題為"基本的
        panel = QGroupBox("3D重建")
        layout = QVBoxLayout()  # 創建垂直佈局

        # 上顎模型檔案選擇（這裡實際上是2D圖檔）
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("2D圖檔"))  # 添加標籤
        self.image_file = QLineEdit()  # 創建輸入框
        image_layout.addWidget(self.image_file)  # 添加輸入框到佈局
        image_button = QPushButton("選擇")  # 創建選擇按鈕
        image_button.clicked.connect(self.choose_image_file)  # 綁定點擊事件到選擇圖檔函數
        image_layout.addWidget(image_button)  # 添加按鈕到佈局
        layout.addLayout(image_layout)  # 添加圖檔選擇佈局到主佈局

        # 下顎模型檔案選擇（3D參考模型）
        lower_layout = QHBoxLayout()
        lower_layout.addWidget(QLabel("3D參考"))  # 添加標籤
        self.lower_file = QLineEdit()  # 創建輸入框
        lower_layout.addWidget(self.lower_file)  # 添加輸入框到佈局
        lower_button = QPushButton("選擇")  # 創建選擇按鈕
        lower_button.clicked.connect(self.choose_lower_file)  # 綁定點擊事件到選擇3D文件函數
        lower_layout.addWidget(lower_button)  # 添加按鈕到佈局
        layout.addLayout(lower_layout)  # 添加3D參考佈局到主佈局

        # 輸出文件夾選擇
        self.output_layout = QHBoxLayout()
        self.output_folder = QLineEdit()  # 創建輸出文件夾輸入框
        # 使用父類方法創建文件選擇佈局
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder, self.model.set_output_folder)

        # 創建並設置保存按鈕
        save_button = QPushButton("3D重建")
        save_button.clicked.connect(self.save_remesh_file)  # 綁定點擊事件到保存函數
        layout.addWidget(save_button)  # 添加按鈕到佈局

        panel.setLayout(layout)  # 設置面板的佈局
        parent_layout.addWidget(panel)  # 添加面板到父佈局
        return panel  # 返回創建的面板

    # 選擇下顎3D參考文件
    def choose_lower_file(self):
        # 調用父類的 choose_file 方法選擇3D模型文件
        file_path = self.choose_file(self.lower_file, "3D Model Files (*.ply *.stl *.obj)")
        if file_path:  # 如果選擇了文件
            self.model.set_reference_file(file_path)  # 設置模型的參考文件
        else:  # 如果取消選擇
            self.model.reference_file = ""  # 清空參考文件路徑

    # 保存3D重建結果
    def save_remesh_file(self):
        # 調用模型的保存方法並檢查結果
        if self.model.save_remesh_file(self.render_input, self.render_input2):
            print("Depth map saved successfully")  # 成功保存深度圖
        else:
            print("Failed to save depth map")  # 保存失敗

    # 選擇2D圖檔
    def choose_image_file(self):
        # 調用父類的 choose_image 方法選擇圖片文件
        file_path = self.choose_image(self.image_file)
        if file_path:  # 如果選擇了文件
            self.model.set_image_file(file_path)  # 設置模型的圖片文件
        else:  # 如果取消選擇
            self.model.image_file = ""  # 清空圖片文件路徑

    # 更新視圖內容
    def update_view(self):
        self.image_file.setText(self.model.image_file)  # 更新2D圖檔路徑顯示
        self.lower_file.setText(self.model.reference_file)  # 更新3D參考文件路徑顯示
        self.output_folder.setText(self.model.output_folder)  # 更新輸出文件夾路徑顯示
        self.render_input.RemoveAllViewProps()  # 清除所有視圖中的演員（actors）
        if self.model.image_file:  # 如果存在圖片文件
            # 在第二窗口渲染圖片文件
            readmodel.render_file_in_second_window(self.render_input, self.model.image_file)