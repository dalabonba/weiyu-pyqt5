# singledepthview.py
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from .baseview import BaseView  
from Otherfunction import readmodel

class AimodelView(BaseView):
    def __init__(self, parent_layout, model, renderinput,renderinput2):
        super().__init__(parent_layout, renderinput,renderinput2)
        self.model = model
        model.model_updated.connect(self.update_view)


    def create_predict(self,parent_layout,current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("AI預測")
        layout = QVBoxLayout()

        # 上顎模型檔案選擇
        self.model_file = QLineEdit()
        self.create_file_selection_layout(layout, "預訓練模型:", self.model_file,self.model.set_model_folder)

        # 下顎模型檔案選擇
        lower_layout = QHBoxLayout()
        lower_layout.addWidget(QLabel("缺陷圖檔:"))
        self.image_file = QLineEdit()
        lower_layout.addWidget(self.image_file)
        lower_button = QPushButton("選擇")
        lower_button.clicked.connect(self.choose_image_file) 
        lower_layout.addWidget(lower_button)
        layout.addLayout(lower_layout)


        # 輸出深度圖文件夾選擇
        self.output_layout = QHBoxLayout()
        self.output_folder = QLineEdit()
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder,self.model.set_output_folder)

        # 保存按鈕
        save_button = QPushButton("AI預測")
        save_button.clicked.connect(self.save_ai_file) 
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel


    def choose_image_file(self):
        file_path = self.choose_image(self.image_file)
        if file_path :
            self.model.set_image_file(file_path)
        else:
            self.model.image_file = ""


    def save_ai_file(self):
        if self.model.save_ai_file(self.render_input,self.render_input2):
            print("Depth map saved successfully")
        else:
            print("Failed to save depth map")


    def update_view(self):
        self.render_input.RemoveAllViewProps()  # Clear all actors
        self.model_file.setText(self.model.model_folder)
        self.image_file.setText(self.model.image_file)
        self.output_folder.setText(self.model.output_folder)
        if self.model.image_file:
            readmodel.render_png_in_second_window(self.render_input,self.model.image_file)
