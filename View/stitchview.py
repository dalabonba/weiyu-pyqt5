
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from .baseview import BaseView  
from Otherfunction import readmodel

class StitchView(BaseView):
    def __init__(self, parent_layout, model, renderinput,renderinput2):
        super().__init__(parent_layout, renderinput,renderinput2)
        self.model = model

    def create_predict(self,parent_layout,current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("AI預測")
        layout = QVBoxLayout()

        lower_layout, self.threeddown_file = self.create_file_selector(
        "下顎缺陷3D模型:", panel, "3D Model Files (*.ply *.stl *.obj)","down"
        )
        upper_layout, self.threedupper_file = self.create_file_selector(
        "上顎3D模型:", panel, "3D Model Files (*.ply *.stl *.obj)","up"
        )
        layout.addLayout(lower_layout)
        layout.addLayout(upper_layout)


        self.model_file = QLineEdit()
        self.create_file_selection_layout(layout, "預訓練模型:", self.model_file,self.model.set_model_folder)


        # 輸出深度圖文件夾選擇
        self.output_folder = QLineEdit()
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder,self.model.set_output_folder)

        # 保存按鈕
        save_button = QPushButton("AI預測")
        save_button.clicked.connect(self.save_ai_file) 
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel
    
    def create_file_selector(self,label_text, parent, file_types,position_type):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        layout.addWidget(label)
        file_input = QLineEdit()
        layout.addWidget(file_input)
        button = QPushButton("選擇")
        button.clicked.connect(lambda: self.choose_file(file_input, file_types,position_type))
        layout.addWidget(button)
        return layout, file_input
    
    def save_stitch_model(self):
            output_file_path=self.model.save_stitch_model(self.render_input)
            readmodel.render_file_in_second_window(self.render_input2,output_file_path)
            self.model.reset(self.render_input2)
            print("Depth map saved successfully")