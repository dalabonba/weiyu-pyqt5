from PyQt5.QtCore import  pyqtSignal
import os
from .BaseModel import BaseModel
from Otherfunction import readmodel,trianglegood

class RemeshModel(BaseModel):
    model_updated = pyqtSignal()  # Define the signal at the class level
    
    def __init__(self):
        super().__init__()  # Make sure to call the superclass constructor
        self.image_file = ""
        self.reference_file = ""
        self.output_folder = ""


    def set_reference_file(self, file_path):
        if os.path.exists(file_path):
            self.reference_file = file_path
            self.model_updated.emit()
            return True
        return False

    def set_image_file(self, file_path):
        if os.path.exists(file_path):
            self.image_file = file_path
            self.model_updated.emit()
            return True
        return False
    
    def save_remesh_file(self,renderer,render2):
        if self.image_file and  self.output_folder and self.reference_file:
            image_file_cleaned = self.image_file.strip("' ").strip()
            base_name = os.path.splitext(os.path.basename(image_file_cleaned))[0]
            output_stl_path = self.output_folder+'/'+base_name+".stl"
            trianglegood.DentalModelReconstructor(self.image_file,self.reference_file,output_stl_path).reconstruct()
            readmodel.render_file_in_second_window(render2,output_stl_path)
        return True