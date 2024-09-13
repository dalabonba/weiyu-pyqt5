from PyQt5.QtCore import QObject, pyqtSignal
import os
from Otherfunction import readmodel
class SingleDepthModel(QObject):
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
            self.model_updated.emit()  # Emit the signal
            return True
        return False

    def set_lower_file(self, file_path):
        if os.path.exists(file_path):
            self.lower_file = file_path
            self.model_updated.emit()  # Emit the signal
            return True
        return False

    def set_output_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.output_folder = folder_path
            self.model_updated.emit()  # Emit the signal
            return True
        return False

    def set_upper_opacity(self, opacity):
        self.upper_opacity = opacity
        if self.upper_actor:
            self.upper_actor.GetProperty().SetOpacity(opacity)
        self.model_updated.emit()  # Emit the signal

    def set_lower_opacity(self, opacity):
        self.lower_opacity = opacity
        if self.lower_actor:
            self.lower_actor.GetProperty().SetOpacity(opacity)
        self.model_updated.emit()  # Emit the signal

    def set_model_angle(self, angle):
        self.angle = angle
        if self.upper_actor and self.lower_actor:
            readmodel.rotate_actor(self.upper_actor, self.models_center,self.angle)
            readmodel.rotate_actor(self.lower_actor, self.models_center,self.angle)
        else:
            if self.upper_actor:
                readmodel.rotate_actor(self.upper_actor, self.models_center,self.angle)
            if self.lower_actor:
                readmodel.rotate_actor(self.lower_actor, self.lower_center,self.angle)
        self.model_updated.emit()

    def render_model(self,renderer,type):
        renderer.RemoveAllViewProps()
        self.upper_actor = None
        self.lower_actor = None
        if type == 'up' or self.upper_file:
            model1 = readmodel.load_3d_model(self.upper_file)
            self.upper_actor = readmodel.create_actor(model1, (1, 0, 0))  # Red color
            self.upper_actor.GetProperty().SetOpacity(self.upper_opacity)
            self.upper_center = readmodel.calculate_center(self.upper_actor)
            renderer.AddActor(self.upper_actor)
        if type == 'down' or self.lower_file:
            model2 = readmodel.load_3d_model(self.lower_file)
            self.lower_actor = readmodel.create_actor(model2, (0, 1, 0))  # Green color
            self.lower_actor.GetProperty().SetOpacity(self.lower_opacity)
            self.lower_center = readmodel.calculate_center(self.lower_actor)
            renderer.AddActor(self.lower_actor)
        if  self.lower_file and  self.upper_file:
            self.models_center = readmodel.twomodel_bound(self.lower_actor.GetBounds(),self.upper_actor.GetBounds())

        renderer.ResetCamera() 
        renderer.GetRenderWindow().Render()
        
        # print(f"Rendering model with upper file: {self.upper_file} and lower file: {self.lower_file}")
        # print(f"Upper opacity: {self.upper_opacity}, Lower opacity: {self.lower_opacity}")
        # In a real implementation, this method would return the rendered model or update a view



    def save_depth_map(self):
        if not self.output_folder:
            print("Output folder not set")
            return False
        print(f"Saving depth map to {self.output_folder}")
        # In a real implementation, this method would actually save the depth map
        return True
    