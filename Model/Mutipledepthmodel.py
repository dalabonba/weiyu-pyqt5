from PyQt5.QtCore import QObject, pyqtSignal
import os

class BatchDepthModel(QObject):
    model_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.upper_folder = ""
        self.lower_folder = ""
        self.angle=0
        self.output_folder = ""
        self.upper_opacity = 1.0
        self.lower_opacity = 1.0
        self.upper_files = []
        self.lower_files = []

    def set_upper_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.upper_folder = folder_path
            self.upper_files = self._get_files_in_folder(folder_path)
            self.model_updated.emit()
            return True
        return False

    def set_lower_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.lower_folder = folder_path
            self.lower_files = self._get_files_in_folder(folder_path)
            self.model_updated.emit()
            return True
        return False

    def set_output_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.output_folder = folder_path
            self.model_updated.emit()
            return True
        return False

    def set_upper_opacity(self, opacity):
        self.upper_opacity = opacity
        self.model_updated.emit()

    def set_lower_opacity(self, opacity):
        self.lower_opacity = opacity
        self.model_updated.emit()

    def _get_files_in_folder(self, folder_path):
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    def render_models(self):
        if not self.upper_files or not self.lower_files:
            print("Upper or lower files not set")
            return False

        for upper_file, lower_file in zip(self.upper_files, self.lower_files):
            upper_path = os.path.join(self.upper_folder, upper_file)
            lower_path = os.path.join(self.lower_folder, lower_file)
            print(f"Rendering model with upper file: {upper_path} and lower file: {lower_path}")
            print(f"Upper opacity: {self.upper_opacity}, Lower opacity: {self.lower_opacity}")
            # In a real implementation, this method would render the model for each pair of files

        return True

    def save_depth_map(self):
        if not self.output_folder:
            print("Output folder not set")
            return False

        if not self.upper_files or not self.lower_files:
            print("Upper or lower files not set")
            return False

        for upper_file, lower_file in zip(self.upper_files, self.lower_files):
            output_file = f"depth_map_{os.path.splitext(upper_file)[0]}.png"
            output_path = os.path.join(self.output_folder, output_file)
            print(f"Saving depth map to {output_path}")
            # In a real implementation, this method would actually save the depth map for each pair of files

        return True