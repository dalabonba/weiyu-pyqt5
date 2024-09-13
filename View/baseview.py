# baseview.py
from PyQt5.QtWidgets import QFileDialog

class BaseView:
    def __init__(self, parent_layout,renderinput):
        self.parent_layout = parent_layout  # 父布局
        self.render_input=renderinput
    def choose_file(self, line_edit):
        options = QFileDialog.Options()
        file_filter = "3D Model Files (*.ply *.stl *.obj)"
        file_path, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", file_filter, options=options)
        if file_path:
            line_edit.setText(file_path)
        else:
            line_edit.setText(None)
        return file_path

    def choose_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(None, "選擇文件夾")
        if folder:
            line_edit.setText(folder)
            return folder

    def save_function_file(self):
        # Implement the logic to save the depth map
        print(f"Saving depth map...")
        print(f"Upper model: {self.upper_file.text()}")
        print(f"Lower model: {self.lower_file.text()}")
        print(f"Upper opacity: {self.upper_opacity.value()}%")
        print(f"Lower opacity: {self.lower_opacity.value()}%")
        print(f"Output folder: {self.output_folder.text()}")

    def update_angle(self):
        try:
            angle = float(self.angle_input.text())
            self.model.set_model_angle(angle)
        except ValueError:
            print("Invalid angle input")
