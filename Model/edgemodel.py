from PyQt5.QtCore import  pyqtSignal
from .BaseModel import BaseModel
from pathlib import Path
from Otherfunction import readmodel,pictureedgblack,twopicturedege
import os


class EdgeModel(BaseModel):
    model_updated = pyqtSignal()  # Define the signal at the class level
    
    def __init__(self):
        super().__init__()  # Make sure to call the superclass constructor
        self.upper_file = ""
        self.lower_file = ""
        self.output_folder = ""
        self.upper_files = []
        self.lower_files = []


    def save_edge_button(self,renderer,render2):
        for upper_file in (self.lower_files):
            render2.GetRenderWindow().Render()
            render2.ResetCamera()
            render2.RemoveAllViewProps()
            self.upper_file = ""
            self.lower_file = ""
            self.upper_file = (Path(self.upper_folder)/upper_file).as_posix()
            readmodel.render_file_in_second_window(renderer,self.upper_file)
            pictureedgblack.mark_boundary_points(self.upper_file,self.output_folder+"/edgeUp", color=(255, 255, 0))
            readmodel.render_file_in_second_window(render2,self.output_folder+"/edgeUp/"+upper_file)
        for  lower_file in  self.lower_files:
            render2.GetRenderWindow().Render()
            render2.ResetCamera()
            render2.RemoveAllViewProps()
            self.upper_file = ""
            self.lower_file = ""
            self.lower_file = (Path(self.lower_folder)/lower_file).as_posix()
            readmodel.render_file_in_second_window(renderer,self.lower_file)
            pictureedgblack.mark_boundary_points(self.lower_file,self.output_folder+"/edgeDown")
            readmodel.render_file_in_second_window(render2,self.output_folder+"/edgeDown/"+lower_file)
        red_image_files = os.listdir(self.output_folder+"/edgeDown/")
        for image in red_image_files :
            twopicturedege.combine_image(self.output_folder+"/edgeDown/"+image
                                         , self.output_folder+"/edgeUp/"+image
                                         , self.output_folder+"/combinetwoedge/"
                                         ,(Path(self.lower_folder)/image).as_posix()
                                         ,(Path(self.upper_folder)/image).as_posix())
        return True
