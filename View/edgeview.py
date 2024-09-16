# singledepthview.py
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import Qt
from .baseview import BaseView  

class ImageedgeView(BaseView):
    def __init__(self, parent_layout, model, renderinput,renderinput2):
        super().__init__(parent_layout, renderinput,renderinput2) 
        self.model = model

    def create_edge(self,parent_layout,current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("批次創建牙齒邊界線")
        layout = QVBoxLayout()

        # 上顎模型檔案選擇
        self.upper_file = QLineEdit()
        self.create_file_selection_layout(layout, "上顎圖檔:", self.upper_file,self.model.set_upper_folder)


        # 下顎模型檔案選擇
        self.lower_file = QLineEdit()
        self.create_file_selection_layout(layout, "下顎圖檔:", self.lower_file,self.model.set_lower_folder)


        # 輸出深度圖文件夾選擇
        self.output_layout = QHBoxLayout()
        self.output_folder = QLineEdit()
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder,self.model.set_output_folder)

        # 保存按鈕
        save_button = QPushButton("保存邊界線圖")
        save_button.clicked.connect(self.save_edge_file) 
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel


    def update_view(self):
        # Update the view based on the model's current state
        self.upper_file.setText(self.model.upper_folder)
        self.lower_file.setText(self.model.lower_folder)
        self.output_folder.setText(self.model.output_folder)

    def save_edge_file(self):
        if self.model.save_edge_button(self.render_input,self.render_input2):
            print("Depth map saved successfully")
        else:
            print("Failed to save depth map")