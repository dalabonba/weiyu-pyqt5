from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import Qt
from .baseview import BaseView  
from Otherfunction import readmodel

class SingleDepthView(BaseView):
    def __init__(self, parent_layout, model, renderinput, renderinput2):
        super().__init__(parent_layout, renderinput, renderinput2)  # 初始化基礎視圖
        self.model = model
        model.model_updated.connect(self.update_view)  # 連接模型更新信號

    def create_depth(self, parent_layout, current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)  # 移除當前面板

        panel = QGroupBox("單次創建深度圖")  # 創建組框
        layout = QVBoxLayout()

        # 上顎模型檔案選擇
        upper_layout = QHBoxLayout()
        upper_layout.addWidget(QLabel("上顎檔案:"))
        self.upper_file = QLineEdit()
        upper_layout.addWidget(self.upper_file)
        upper_button = QPushButton("選擇")
        upper_button.clicked.connect(self.choose_upper_file)  # 設定選擇文件功能
        upper_layout.addWidget(upper_button)
        layout.addLayout(upper_layout)

        # 下顎模型檔案選擇
        lower_layout = QHBoxLayout()
        lower_layout.addWidget(QLabel("下顎檔案:"))
        self.lower_file = QLineEdit()
        lower_layout.addWidget(self.lower_file)
        lower_button = QPushButton("選擇")
        lower_button.clicked.connect(self.choose_lower_file)  # 設定選擇文件功能
        lower_layout.addWidget(lower_button)
        layout.addLayout(lower_layout)

        # 旋轉角度輸入框
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("旋轉角度:"))
        self.angle_input = QLineEdit()
        self.angle_input.setText("0")
        self.angle_input.editingFinished.connect(self.update_angle)  # 設定角度更新
        angle_layout.addWidget(self.angle_input)
        layout.addLayout(angle_layout)

        # 上顎透明度調整滑塊
        upper_opacity_layout = QHBoxLayout()
        upper_opacity_layout.addWidget(QLabel("上顎透明度:"))
        self.upper_opacity = QSlider(Qt.Horizontal)
        self.upper_opacity.setRange(0, 1)
        self.upper_opacity.setValue(1)
        self.upper_opacity.valueChanged.connect(self.update_upper_opacity)
        upper_opacity_layout.addWidget(self.upper_opacity)
        layout.addLayout(upper_opacity_layout)

        # 下顎透明度調整滑塊
        lower_opacity_layout = QHBoxLayout()
        lower_opacity_layout.addWidget(QLabel("下顎透明度:"))
        self.lower_opacity = QSlider(Qt.Horizontal)
        self.lower_opacity.setRange(0, 1)
        self.lower_opacity.setValue(1)
        self.lower_opacity.valueChanged.connect(self.update_lower_opacity)
        lower_opacity_layout.addWidget(self.lower_opacity)
        layout.addLayout(lower_opacity_layout)

        # 輸出深度圖文件夾選擇
        self.output_layout = QHBoxLayout()
        self.output_folder = QLineEdit()
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder, self.model.set_output_folder)

        # 保存深度圖按鈕
        save_button = QPushButton("保存深度圖")
        save_button.clicked.connect(self.save_depth_single_map)
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel
 
    def choose_upper_file(self):
        file_path = self.choose_file(self.upper_file, "3D Model Files (*.ply *.stl *.obj)")
        if file_path and self.model.set_upper_file(file_path):
            self.model.render_model(self.render_input)
        else:
            # 若無效則移除上顎模型
            if hasattr(self.model, 'upper_actor') and self.model.upper_actor:
                self.render_input.RemoveActor(self.model.upper_actor)
                self.render_input.ResetCamera()
                self.render_input.GetRenderWindow().Render()
            self.model.upper_file = ""
            self.model.upper_center = None
            self.model.models_center = None

    def choose_lower_file(self):
        file_path = self.choose_file(self.lower_file, "3D Model Files (*.ply *.stl *.obj)")
        if file_path and self.model.set_lower_file(file_path):
            self.model.render_model(self.render_input)
        else:
            # 若無效則移除下顎模型
            if hasattr(self.model, 'lower_actor') and self.model.lower_actor:
                self.render_input.RemoveActor(self.model.lower_actor)
                self.render_input.ResetCamera()
                self.render_input.GetRenderWindow().Render()
            self.model.lower_file = ""
            self.model.lower_center = None
            self.model.models_center = None

    def update_upper_opacity(self):
        opacity = self.upper_opacity.value() 
        self.model.set_upper_opacity(opacity)  # 設定上顎透明度

    def update_lower_opacity(self):
        opacity = self.lower_opacity.value()
        self.model.set_lower_opacity(opacity)  # 設定下顎透明度

    def save_depth_single_map(self):
        output_file_path = self.model.save_depth_map(self.render_input)
        readmodel.render_file_in_second_window(self.render_input2, output_file_path)
        print("Depth map saved successfully")

    def update_view(self):
        # 更新 UI 以反映模型的當前狀態
        self.upper_file.setText(self.model.upper_file)
        self.lower_file.setText(self.model.lower_file)
        self.angle_input.setText(str(self.model.angle))
        self.output_folder.setText(self.model.output_folder)
        self.upper_opacity.setValue(int(self.model.upper_opacity))
        self.lower_opacity.setValue(int(self.model.lower_opacity))
        self.render_input.ResetCamera()
        self.render_input.GetRenderWindow().Render()
