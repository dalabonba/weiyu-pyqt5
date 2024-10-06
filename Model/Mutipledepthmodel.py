from PyQt5.QtCore import  pyqtSignal
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


    def set_upper_opacity(self, opacity):
        self.upper_opacity = opacity
        self.model_updated.emit()

    def set_lower_opacity(self, opacity):
        self.lower_opacity = opacity
        self.model_updated.emit()

    # def set_model_angle(self, angle):
    #     self.angle = angle
    #     self.model_updated.emit()
    
    def save_depth_map_button(self,renderer,render2):
        if self.upper_folder == "":
            for  lower_file in  self.lower_files:
                render2.GetRenderWindow().Render()
                render2.ResetCamera()
                render2.RemoveAllViewProps()
                self.lower_file = (Path(self.lower_folder)/lower_file).as_posix()
                if not self.lower_file:
                    pass
                if self.lower_file:
                    self.render_model(renderer)
                self.set_model_angle(self.angle)
                self.save_depth_map(renderer,render2)
        else:
            for upper_file, lower_file in zip(self.upper_files, self.lower_files):
                render2.GetRenderWindow().Render()
                render2.ResetCamera()
                render2.RemoveAllViewProps()
                self.upper_file = (Path(self.upper_folder)/upper_file).as_posix()
                self.lower_file = (Path(self.lower_folder)/lower_file).as_posix()
                if not self.lower_file:
                    pass
                if self.lower_file:
                    self.render_model(renderer)
                if self.upper_file:
                    self.render_model(renderer)
                self.set_model_angle(self.angle)
                self.save_depth_map(renderer,render2)

        return True
    
