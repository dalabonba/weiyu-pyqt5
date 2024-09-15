from PyQt5.QtCore import  pyqtSignal
import os
from .BaseModel import BaseModel
class SingleDepthModel(BaseModel):
    model_updated = pyqtSignal()  # Define the signal at the class level
    
    def __init__(self):
        super().__init__()  # Make sure to call the superclass constructor
        self.upper_file = ""
        self.lower_file = ""
        self.angle=0
        self.output_folder = ""
        self.upper_opacity = 1.0
        self.lower_opacity = 1.0
        self.upper_center = None
        self.lower_center = None
        self.models_center = None



    def set_upper_file(self, file_path):
        if os.path.exists(file_path):
            self.upper_file = file_path
            self.upper_center = None  # Reset center when new file is set
            self.models_center = None
            self.model_updated.emit()
            return True
        return False

    def set_lower_file(self, file_path):
        if os.path.exists(file_path):
            self.lower_file = file_path
            self.lower_center = None  # Reset center when new file is set
            self.models_center = None
            self.model_updated.emit()
            return True
        return False
    
    def set_output_folder(self, file_path ):
        if os.path.exists(file_path):
            self.output_folder = file_path
            self.model_updated.emit()  # Emit the signal
            return True
        return False

    def set_upper_opacity(self, opacity):
        self.upper_opacity = opacity
        if (hasattr(self, 'upper_actor')and self.upper_actor):
            self.upper_actor.GetProperty().SetOpacity(opacity)
        self.model_updated.emit()  # Emit the signal

    def set_lower_opacity(self, opacity):
        self.lower_opacity = opacity
        if (hasattr(self, 'upper_actor')and self.upper_actor):
            self.lower_actor.GetProperty().SetOpacity(opacity)
        self.model_updated.emit()  # Emit the signal



