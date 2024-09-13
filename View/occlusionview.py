
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import Qt
from .baseview import BaseView  

class OcclusionView(BaseView):
    def __init__(self, parent_layout, model, renderinput):
        super().__init__(parent_layout, renderinput)
        self.model = model

    def create_depth(self,parent_layout,current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("批次創建上下顎咬合圖")
        layout = QVBoxLayout()

        # 上顎模型檔案選擇
        upper_layout = QHBoxLayout()
        upper_layout.addWidget(QLabel("上顎圖檔:"))
        self.upper_file = QLineEdit()
        upper_layout.addWidget(self.upper_file)
        upper_button = QPushButton("選擇")
        upper_button.clicked.connect(lambda: self.choose_folder(self.upper_file))  # 使用 BaseView 的 choose_file
        upper_layout.addWidget(upper_button)
        layout.addLayout(upper_layout)

        # 下顎模型檔案選擇
        lower_layout = QHBoxLayout()
        lower_layout.addWidget(QLabel("下顎圖檔:"))
        self.lower_file = QLineEdit()
        lower_layout.addWidget(self.lower_file)
        lower_button = QPushButton("選擇")
        lower_button.clicked.connect(lambda: self.choose_folder(self.lower_file))  # 使用 BaseView 的 choose_file
        lower_layout.addWidget(lower_button)
        layout.addLayout(lower_layout)


        # 輸出深度圖文件夾選擇
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("輸出文件夾:"))
        self.output_folder = QLineEdit()
        output_layout.addWidget(self.output_folder)
        output_button = QPushButton("選擇")
        output_button.clicked.connect(lambda: self.choose_folder(self.output_folder))  # 使用 BaseView 的 choose_folder
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)

        # 保存按鈕
        save_button = QPushButton("保存咬合圖")
        save_button.clicked.connect(self.save_function_file)  # 使用 BaseView 的 save_depth_map
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel
