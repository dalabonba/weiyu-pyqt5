# singledepthview.py
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from .baseview import BaseView  
from Otherfunction import readmodel
import time

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

        # 創建帶標題的組框，標題為"3D重建"
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
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder, self.model.set_output_folder)

        # 第一排：選擇模式 (BB 或 OBB)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("模式選擇:"))  # 添加標籤
        self.mode_combo = QComboBox()  # 創建下拉選單
        self.mode_combo.addItems(["", "BB", "OBB"])  # 添加選項，"" 表示未選擇
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)  # 綁定模式改變事件
        mode_layout.addWidget(self.mode_combo)  # 添加下拉選單到佈局
        layout.addLayout(mode_layout)  # 添加模式選擇佈局到主佈局

        # 第二排：選擇面 (咬合面、舌側、頰側)
        face_layout = QHBoxLayout()
        face_layout.addWidget(QLabel("面選擇:"))  # 添加標籤
        self.face_combo = QComboBox()  # 創建下拉選單
        self.face_combo.addItems(["", "咬合面", "舌側", "頰側"])  # 添加選項，"" 表示未選擇
        self.face_combo.setEnabled(False)  # 初始禁用
        self.face_combo.currentTextChanged.connect(self.on_face_changed)  # 綁定面改變事件
        face_layout.addWidget(self.face_combo)  # 添加下拉選單到佈局
        layout.addLayout(face_layout)  # 添加面選擇佈局到主佈局

        # 創建並設置保存按鈕
        save_button = QPushButton("3D重建")
        save_button.clicked.connect(self.save_remesh_file)  # 綁定點擊事件到保存函數
        layout.addWidget(save_button)  # 添加按鈕到佈局

        panel.setLayout(layout)  # 設置面板的佈局
        parent_layout.addWidget(panel)  # 添加面板到父佈局
        return panel  # 返回創建的面板

    # 選擇下顎3D參考文件
    def choose_lower_file(self):
        file_path = self.choose_file(self.lower_file, "3D Model Files (*.ply *.stl *.obj)")
        if file_path:
            self.model.set_reference_file(file_path)
        else:
            self.model.reference_file = ""

    # 選擇2D圖檔
    def choose_image_file(self):
        file_path = self.choose_image(self.image_file)
        if file_path:
            self.model.set_image_file(file_path)
        else:
            self.model.image_file = ""

    # 當模式改變時觸發
    def on_mode_changed(self, mode):
        if mode:  # 如果選擇了有效模式（非空）
            self.model.set_mode(mode)  # 設置模型的模式
            self.face_combo.setEnabled(True)  # 啟用面選擇下拉選單
        else:
            self.model.mode = None  # 清空模式
            self.face_combo.setEnabled(False)  # 禁用面選擇下拉選單
            self.face_combo.setCurrentText("")  # 重置面選擇

    # 當面改變時觸發
    def on_face_changed(self, face):
        if face:  # 如果選擇了有效面（非空）
            self.model.set_face(face)  # 設置模型的面
        else:
            self.model.face = None  # 清空面選擇

    # 保存3D重建結果
    def save_remesh_file(self):
        start_time = time.time()
        if self.model.save_remesh_file(self.render_input, self.render_input2):
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Depth map saved successfully in {elapsed_time:.2f} seconds")
        else:
            print("Failed to save depth map")

    # 更新視圖內容
    def update_view(self):
        self.image_file.setText(self.model.image_file)
        self.lower_file.setText(self.model.reference_file)
        self.output_folder.setText(self.model.output_folder)
        self.render_input.RemoveAllViewProps()
        if self.model.image_file:
            readmodel.render_file_in_second_window(self.render_input, self.model.image_file)
        # 更新模式和面的顯示
        self.mode_combo.setCurrentText(self.model.mode if self.model.mode else "")
        self.face_combo.setCurrentText(self.model.face if self.model.face else "")
        self.face_combo.setEnabled(bool(self.model.mode))  # 根據模式是否選擇啟用面選項