from PyQt5.QtCore import QObject
import os
from Otherfunction import readmodel,pictureedgblack,fillwhite

class BaseModel(QObject):
    def __init__(self):
        super().__init__()


    def set_model_angle(self, angle):
        self.angle = angle
        if not hasattr(self, 'lower_actor'):
            self.model_updated.emit()
            return
        if self.lower_actor and not hasattr(self, 'upper_actor'):
                self.lower_center = readmodel.calculate_center(self.lower_actor)
                readmodel.rotate_actor(self.lower_actor, self.lower_center,self.angle)
        elif self.upper_file!='' and self.lower_actor:
            readmodel.rotate_actor(self.upper_actor, self.models_center,self.angle)
            readmodel.rotate_actor(self.lower_actor, self.models_center,self.angle)
        else:
            self.lower_center = readmodel.calculate_center(self.lower_actor)
            readmodel.rotate_actor(self.lower_actor, self.lower_center,self.angle)
        # else:
        #     if self.upper_actor:
        #         self.upper_center = readmodel.calculate_center(self.upper_actor)
        #         readmodel.rotate_actor(self.upper_actor, self.upper_center,self.angle)

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
        renderer.GetRenderWindow().Render()


    def save_depth_map(self,renderer,render2):
        renderer.GetRenderWindow().SetSize(256, 256)
        if self.lower_actor and  self.output_folder:
            lower_bound = self.lower_actor.GetBounds()
            upper_file_cleaned = self.upper_file.strip("' ").strip()
            # Extract the file name without the extension from self.upper_file
            base_name = os.path.splitext(os.path.basename(upper_file_cleaned))[0]
            
            # Create the output file path
            output_file_path = self.output_folder+'/'+base_name+".png"
            if self.upper_opacity == 0 :
                scale_filter=readmodel.setup_camera(renderer,renderer.GetRenderWindow()
                                    ,self.lower_center,self.upper_center,lower_bound,self.upper_opacity)
                readmodel.save_depth_image(output_file_path,scale_filter)
                bound=pictureedgblack.get_image_bound(output_file_path)
                fillwhite.process_image_pair(bound,output_file_path,output_file_path)
            else:
                scale_filter=readmodel.setup_camera(renderer,renderer.GetRenderWindow()
                                ,self.lower_center,self.upper_center,lower_bound,self.upper_opacity)
                readmodel.save_depth_image(output_file_path,scale_filter)
            renderer.GetRenderWindow().SetSize(768, 768)
            readmodel.render_png_in_second_window(render2,output_file_path)
            self.reset()
        else:
            print("Output folder not set")
        print(f"Saving depth map to {self.output_folder}")
        # In a real implementation, this method would actually save the depth map
        return True
    

    def set_output_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.output_folder = folder_path
            self.model_updated.emit()
            return True
        return False
    
    def reset(self):
        self.upper_file = ""
        self.lower_file = ""
        self.angle = 0
        self.upper_center = None
        self.lower_center = None
        self.models_center = None

        if hasattr(self, 'upper_actor'):
            del self.upper_actor
        if hasattr(self, 'lower_actor'):
            del self.lower_actor
        self.model_updated.emit()