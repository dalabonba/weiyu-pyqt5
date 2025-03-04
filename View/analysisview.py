# singledepthview.py
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import Qt
from .baseview import BaseView  

class AnalysisView(BaseView):
    def __init__(self, parent_layout, model, renderinput,renderinput2):
        super().__init__(parent_layout, renderinput,renderinput2) 
        self.model = model

    def create_edge(self,parent_layout,current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("遮罩贋復區域分析")
        layout = QVBoxLayout()

        # 真實檔案選擇
        self.groudtruth_file = QLineEdit()
        self.create_file_selection_layout(layout, "真實圖檔資料夾:", self.groudtruth_file,
                                          self.model.set_groudtruth_folder)


        # 修復檔案選擇
        self.result_file = QLineEdit()
        self.create_file_selection_layout(layout, "修復圖檔資料夾:", self.result_file,
                                          self.model.set_result_folder)
        
        # 修復檔案選擇
        self.mask_file = QLineEdit()
        self.create_file_selection_layout(layout, "遮罩圖檔資料夾:", self.mask_file,
                                          self.model.set_mask_folder)


        # 輸出深度圖文件夾選擇
        self.output_layout = QHBoxLayout()
        self.output_folder = QLineEdit()
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder,
                                          self.model.set_output_folder)

        # 保存按鈕
        save_button = QPushButton("保存分析數值")
        save_button.clicked.connect(self.save_value_file) 
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel


    def update_view(self):
        # Update the view based on the model's current state
        self.groudtruth_file.setText(self.model.groudtruth_file)
        self.result_file.setText(self.model.result_file)
        self.mask_file.setText(self.model.mask_file)
        self.output_folder.setText(self.model.output_folder)

    def save_value_file(self):
        if self.model.save_value_button(self.render_input,self.render_input2):
            print("Depth map saved successfully")
        else:
            print("Failed to save depth map")