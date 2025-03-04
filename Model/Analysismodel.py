from PyQt5.QtCore import  pyqtSignal
import os
from .BaseModel import BaseModel
from evaluate import elismated,compare
class AnalysisModel(BaseModel):
    model_updated = pyqtSignal()  # Define the signal at the class level
    
    def __init__(self):
        super().__init__()  # Make sure to call the superclass constructor
        self.groudtruth_file = ""
        self.result_file = ""
        self.mask_file = ""
        self.output_folder = ""




    def set_groudtruth_folder(self, file_path):
        if os.path.exists(file_path):
            self.groudtruth_file = file_path
            self.model_updated.emit()
            return True
        return False

    def set_result_folder(self, file_path):
        if os.path.exists(file_path):
            self.result_file = file_path
            self.model_updated.emit()
            return True
        return False
    def set_mask_folder(self, file_path):
        if os.path.exists(file_path):
            self.mask_file = file_path
            self.model_updated.emit()
            return True
        return False
    
    def set_output_folder(self, file_path ):
        if os.path.exists(file_path):
            self.output_folder = file_path
            self.model_updated.emit()  # Emit the signal
            return True
        return False



    def save_value_button(self,renderer,render2):
        r_value = os.path.basename(os.path.normpath(self.result_file))
        output_folder = os.path.join(self.output_folder, f"{r_value}.txt")
        elismated.cal_all(self.groudtruth_file,self.result_file,
                          output_folder,self.mask_file)
        compare.compare_image_folders(self.groudtruth_file,self.result_file,
                                      self.output_folder, image_size=(256, 256))
        return True


