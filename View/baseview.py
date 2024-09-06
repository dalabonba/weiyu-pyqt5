# baseview.py
from PyQt5.QtWidgets import QFileDialog

class BaseView:
    def __init__(self, parent_layout):
        self.parent_layout = parent_layout  # 父布局

    def choose_file(self, line_edit):
        filename, _ = QFileDialog.getOpenFileName(None, "選擇檔案")
        if filename:
            line_edit.setText(filename)

    def choose_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(None, "選擇文件夾")
        if folder:
            line_edit.setText(folder)

    def save_function_file(self):
        # Implement the logic to save the depth map
        print(f"Saving depth map...")
        print(f"Upper model: {self.upper_file.text()}")
        print(f"Lower model: {self.lower_file.text()}")
        print(f"Upper opacity: {self.upper_opacity.value()}%")
        print(f"Lower opacity: {self.lower_opacity.value()}%")
        print(f"Output folder: {self.output_folder.text()}")
