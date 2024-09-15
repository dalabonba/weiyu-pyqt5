from PyQt5.QtCore import  pyqtSignal
import os
from Otherfunction import readmodel
from .BaseModel import BaseModel
from pathlib import Path
class BatchDepthModel(BaseModel):
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
        self.upper_folder = folder_path
        if os.path.isdir(folder_path):
            self.upper_files = self._get_files_in_folder(folder_path)
            self.model_updated.emit()
            return True
        return False

    def set_lower_folder(self, folder_path):
        self.lower_folder = folder_path
        if os.path.isdir(folder_path):
            self.lower_files = self._get_files_in_folder(folder_path)
            self.model_updated.emit()
            return True
        return False



    def set_upper_opacity(self, opacity):
        self.upper_opacity = opacity
        self.model_updated.emit()

    def set_lower_opacity(self, opacity):
        self.lower_opacity = opacity
        self.model_updated.emit()

    def set_model_angle(self, angle):
        self.angle = angle
        self.model_updated.emit()

    def _get_files_in_folder(self, folder_path):
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    
    def save_depth_map_button(self,renderer,render2):
        for upper_file, lower_file in zip(self.upper_files, self.lower_files):
            render2.GetRenderWindow().Render()
            render2.ResetCamera()
            render2.RemoveAllViewProps()
            self.upper_file = ""
            self.upper_center = None
            self.models_center = None
            self.lower_file = ""
            self.lower_center = None
            self.upper_file = (Path(self.upper_folder)/upper_file).as_posix()
            self.lower_file = (Path(self.lower_folder)/lower_file).as_posix()
            if not self.lower_file:
                pass
            if self.lower_file:
                self.render_model(renderer,'down')
            if self.upper_file:
                self.render_model(renderer,'up')
            self.set_model_angle(self.angle)
            self.save_depth_map(renderer,render2)

            # output_file = f"{os.path.splitext(upper_file)[0]}.png"
            # output_path = Path(self.output_folder) / output_file
            # print(f"Saving depth map to {output_path.as_posix()}")
            # In a real implementation, this method would actually save the depth map for each pair of files

        return True
    
