# singledepthview.py
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import Qt
from .baseview import BaseView  
from Otherfunction import readmodel


class RemeshView(BaseView):
    def __init__(self, parent_layout, model, renderinput,renderinput2):
        super().__init__(parent_layout, renderinput,renderinput2) 
        self.model = model
        model.model_updated.connect(self.update_view)

    def create_remesh(self,parent_layout,current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("3D重建")
        layout = QVBoxLayout()

        # 上顎模型檔案選擇
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("2D圖檔"))
        self.image_file = QLineEdit()
        image_layout.addWidget(self.image_file)
        image_button = QPushButton("選擇")
        image_button.clicked.connect(self.choose_image_file)  # 使用 BaseView 的 choose_file
        image_layout.addWidget(image_button)
        layout.addLayout(image_layout)

        # 下顎模型檔案選擇
        lower_layout = QHBoxLayout()
        lower_layout.addWidget(QLabel("3D參考"))
        self.lower_file = QLineEdit()
        lower_layout.addWidget(self.lower_file)
        lower_button = QPushButton("選擇")
        lower_button.clicked.connect(self.choose_lower_file)  # 使用 BaseView 的 choose_file
        lower_layout.addWidget(lower_button)
        layout.addLayout(lower_layout)


        # 輸出深度圖文件夾選擇
        self.output_layout = QHBoxLayout()
        self.output_folder = QLineEdit()
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder,self.model.set_output_folder)

        # 保存按鈕
        save_button = QPushButton("3D重建")
        save_button.clicked.connect(self.save_remesh_file)  # 使用 BaseView 的 save_depth_map
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel


    def choose_lower_file(self):
        # lambda: self.choose_file(self.threed_file, "3D Model Files (*.ply *.stl *.obj)")
        file_path = self.choose_file(self.lower_file, "3D Model Files (*.ply *.stl *.obj)")
        if file_path :
            self.model.set_reference_file(file_path)
        else:
            self.model.reference_file = ""


    def save_remesh_file(self):
        if self.model.save_remesh_file(self.render_input,self.render_input2):
            print("Depth map saved successfully")
        else:
            print("Failed to save depth map")

    def choose_image_file(self):
        file_path = self.choose_image(self.image_file)
        if file_path :
            self.model.set_image_file(file_path)
        else:
            self.model.image_file = ""

    def update_view(self):
        self.image_file.setText(self.model.image_file)
        self.lower_file.setText(self.model.reference_file)
        self.output_folder.setText(self.model.output_folder)
        self.render_input.RemoveAllViewProps()  # Clear all actors
        if self.model.image_file:
            readmodel.render_file_in_second_window(self.render_input,self.model.image_file)