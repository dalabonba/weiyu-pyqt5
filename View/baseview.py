# baseview.py
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import  QHBoxLayout, QLabel,  QPushButton


class BaseView:
    def __init__(self, parent_layout,renderinput,renderinput2):
        self.parent_layout = parent_layout  # 父布局
        self.render_input=renderinput
        self.render_input2=renderinput2

    def choose_file(self, line_edit):
        options = QFileDialog.Options()
        file_filter = "3D Model Files (*.ply *.stl *.obj)"
        file_path, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", file_filter, options=options)
        if file_path:
            line_edit.setText(file_path)
        else:
            line_edit.setText(None)
        return file_path
    


    def choose_image(self, line_edit):
        options = QFileDialog.Options()
        file_filter = " Image (*.png *.jpg *.jpeg)"
        file_path, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", file_filter, options=options)
        if file_path:
            line_edit.setText(file_path)
        else:
            line_edit.setText(None)
        return file_path



    def update_angle(self):
        try:
            angle = float(self.angle_input.text())
            self.model.set_model_angle(angle)
        except ValueError:
            print("Invalid angle input")

    def choose_folder(self, line_edit,set_model_callback):
        folder_path = QFileDialog.getExistingDirectory(None, "選擇文件夾")
        if folder_path:
            set_model_callback(folder_path)
            line_edit.setText(folder_path)
            return folder_path
        else:
            set_model_callback(folder_path)
            line_edit.setText(None)
            return None
    
    def create_file_selection_layout(self, parent_layout, label_text, line_edit,set_model):
        """通用文件夾選擇布局"""
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel(label_text))
        file_layout.addWidget(line_edit)
        button = QPushButton("選擇")
        button.clicked.connect(lambda: self.choose_folder(line_edit,set_model))
        file_layout.addWidget(button)
        parent_layout.addLayout(file_layout)

    def save_function_file(self):
        # Implement the logic to save the depth map
        print(f"Saving depth map...")
        print(f"Upper model: {self.upper_file.text()}")
        print(f"Lower model: {self.lower_file.text()}")
        print(f"Upper opacity: {self.upper_opacity.value()}%")
        print(f"Lower opacity: {self.lower_opacity.value()}%")
        print(f"Output folder: {self.output_folder.text()}")
