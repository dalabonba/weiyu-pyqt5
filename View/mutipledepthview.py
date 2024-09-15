
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import Qt
from .baseview import BaseView


class MutipleDepthView(BaseView): 
    def __init__(self, parent_layout, model, renderinput,renderinput2) :
        super().__init__(parent_layout, renderinput,renderinput2)
        self.model = model
        model.model_updated.connect(self.update_view)

    def create_depth(self,parent_layout,current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("多次創建深度圖")
        layout = QVBoxLayout()

        # 上顎模型檔案選擇
        self.upper_file = QLineEdit()
        self.create_file_selection_layout(layout, "上顎檔案:", self.upper_file,self.model.set_upper_folder)


        # 下顎模型檔案選擇
        self.lower_file = QLineEdit()
        self.create_file_selection_layout(layout, "下顎檔案:", self.lower_file,self.model.set_lower_folder)

        # 旋轉角度輸入
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("旋轉角度:"))
        self.angle_input = QLineEdit()
        self.angle_input.setText("0")
        self.angle_input.textChanged.connect(self.update_angle)
        angle_layout.addWidget(self.angle_input)
        layout.addLayout(angle_layout)

        # 上顎透明度滑塊
        upper_opacity_layout = QHBoxLayout()
        upper_opacity_layout.addWidget(QLabel("上顎透明度:"))
        self.upper_opacity = QSlider(Qt.Horizontal)
        self.upper_opacity.setRange(0, 1)
        self.upper_opacity.setValue(1)
        self.upper_opacity.valueChanged.connect(self.update_upper_opacity)
        upper_opacity_layout.addWidget(self.upper_opacity)
        layout.addLayout(upper_opacity_layout)

        # 下顎透明度滑塊
        lower_opacity_layout = QHBoxLayout()
        lower_opacity_layout.addWidget(QLabel("下顎透明度:"))
        self.lower_opacity = QSlider(Qt.Horizontal)
        self.lower_opacity.setRange(0, 1)
        self.lower_opacity.setValue(1)
        self.lower_opacity.valueChanged.connect(self.update_lower_opacity)
        lower_opacity_layout.addWidget(self.lower_opacity)
        layout.addLayout(lower_opacity_layout)

        # 輸出深度圖文件夾選擇
        self.output_folder = QLineEdit()
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder,self.model.set_output_folder)

        # 保存按鈕
        save_button = QPushButton("保存深度圖")
        save_button.clicked.connect(self.save_depth_maps)
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel

    
    def update_view(self):
        # Update the view based on the model's current state
        self.upper_file.setText(self.model.upper_folder)
        self.lower_file.setText(self.model.lower_folder)
        self.angle_input.setText(str(self.model.angle))
        self.output_folder.setText(self.model.output_folder)
        self.upper_opacity.setValue(int(self.model.upper_opacity ))
        self.lower_opacity.setValue(int(self.model.lower_opacity ))
        camera = self.render_input.GetActiveCamera()
        camera.SetPosition(0, 0, 1)   # 設置相機到初始位置
        camera.SetFocalPoint(0, 0, 0)  # 設置焦點到場景中心
        camera.SetViewUp(0, 1, 0)     # 設置相機的"上"方向
        self.render_input.ResetCamera()
        self.render_input.GetRenderWindow().Render()

    def update_upper_opacity(self):
        opacity = self.upper_opacity.value() 
        self.model.set_upper_opacity(opacity)

    def update_lower_opacity(self):
        opacity = self.lower_opacity.value()
        self.model.set_lower_opacity(opacity)
