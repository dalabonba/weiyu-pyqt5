from PyQt5.QtCore import  pyqtSignal
from .BaseModel import BaseModel
import os
from Otherfunction import readmodel,singleimgcolor
class AipredictModel(BaseModel):
    model_updated = pyqtSignal()  # Define the signal at the class level
    
    def __init__(self):
        super().__init__()  # Make sure to call the superclass constructor
        self.model_folder = ""
        self.image_file = ""
        self.output_folder = ""


    def set_image_file(self, file_path):
        if os.path.exists(file_path):
            self.image_file = file_path
            self.model_updated.emit()
            return True
        return False

    def set_model_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.model_folder = folder_path
            self.model_updated.emit()
            return True
        return False
    
    def save_ai_file(self,renderer,render2):
        renderer.GetRenderWindow().SetSize(256, 256)
        if self.image_file and  self.output_folder and self.model_folder:
            image_file_cleaned = self.image_file.strip("' ").strip()
            base_name = os.path.splitext(os.path.basename(image_file_cleaned))[0]
            output_file_path = self.output_folder+'/ai_'+base_name+".png"
            singleimgcolor.apply_gan_model(self.model_folder, self.image_file, output_file_path)
            readmodel.render_png_in_second_window(render2,output_file_path)
        renderer.GetRenderWindow().SetSize(768, 768)

        return True
    