from PyQt5.QtCore import QObject
import os
from Otherfunction import readmodel,pictureedgblack,fillwhite

class BaseModel(QObject):
    def __init__(self):
        super().__init__()



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
    
    
    def _get_files_in_folder(self, folder_path):
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    def set_model_angle(self, angle):
        self.angle = angle
        if not hasattr(self, 'lower_actor'):
            self.model_updated.emit()
            return
        if hasattr(self, 'upper_actor') and self.lower_actor:
            readmodel.rotate_actor(self.upper_actor, self.models_center,self.angle)
            readmodel.rotate_actor(self.lower_actor, self.models_center,self.angle)
        else:
            self.lower_center = readmodel.calculate_center(self.lower_actor)
            readmodel.rotate_actor(self.lower_actor, self.lower_center,self.angle)
            self.lower_center = readmodel.calculate_center(self.lower_actor)
        self.model_updated.emit()
# 為了確定使用者讀上顎下顎或者上下顎都可以用到
    def render_model(self,renderer):
        renderer.RemoveAllViewProps() 
        if hasattr(self, 'upper_file'):
                if self.upper_file != '':
                    self.model1 = readmodel.load_3d_model(self.upper_file)
                    self.upper_actor = readmodel.create_actor(self.model1, (1, 0, 0))  # Red color
                    self.upper_actor.GetProperty().SetOpacity(self.upper_opacity)
                    self.upper_center = readmodel.calculate_center(self.upper_actor)
                    renderer.AddActor(self.upper_actor)
        if  self.lower_file:
                self.model2 = readmodel.load_3d_model(self.lower_file)
                self.lower_actor = readmodel.create_actor(self.model2, (0, 1, 0))  # Green color
                self.lower_actor.GetProperty().SetOpacity(self.lower_opacity)
                self.lower_center = readmodel.calculate_center(self.lower_actor)
                renderer.AddActor(self.lower_actor)
        if  self.lower_file and  hasattr(self, 'upper_actor'):
            self.models_center = readmodel.twomodel_bound(self.lower_actor.GetBounds(),self.upper_actor.GetBounds())
        renderer.ResetCamera()
        renderer.GetRenderWindow().Render()


    def save_depth_map(self,renderer):
        renderer.GetRenderWindow().SetSize(256, 256)
        if self.lower_actor and  self.output_folder:
            lower_bound = self.lower_actor.GetBounds()
            upper_file_cleaned = self.lower_file.strip("' ").strip()
            # Extract the file name without the extension from self.upper_file
            base_name = os.path.splitext(os.path.basename(upper_file_cleaned))[0]
            
            # Create the output file path
            output_file_path = self.output_folder+'/'+base_name+".png"
            if self.upper_opacity == 0 or not hasattr(self, 'upper_file'):
                scale_filter=readmodel.setup_camera(renderer,renderer.GetRenderWindow()
                                    ,self.lower_center,None,lower_bound,self.upper_opacity,self.angle)
                readmodel.save_depth_image(output_file_path,scale_filter)
                bound=pictureedgblack.get_image_bound(output_file_path)
                fillwhite.process_image_pair(bound,output_file_path,output_file_path)
            else:
                scale_filter=readmodel.setup_camera(renderer,renderer.GetRenderWindow()
                                ,self.lower_center,self.upper_center,lower_bound,self.upper_opacity,self.angle)
                readmodel.save_depth_image(output_file_path,scale_filter)
            renderer.GetRenderWindow().SetSize(768, 768)
            # readmodel.render_file_in_second_window(render2,output_file_path)
            # self.reset(renderer)
        else:
            print("Output folder not set")
        # print(f"Saving depth map to {self.output_folder}")
        # In a real implementation, this method would actually save the depth map
        return output_file_path
    

    def set_output_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.output_folder = folder_path
            self.model_updated.emit()
            return True
        return False
    
    def reset(self,renderer):
        self.upper_file = ""
        self.lower_file = ""
        self.upper_center = None
        self.lower_center = None
        self.models_center = None

        if hasattr(self, 'upper_actor'):
            del self.upper_actor
        if hasattr(self, 'lower_actor'):
            del self.lower_actor
        camera = renderer.GetActiveCamera()
        camera.SetPosition(0, 0, 1)   # 設置相機到初始位置
        camera.SetFocalPoint(0, 0, 0)  # 設置焦點到場景中心
        camera.SetViewUp(0, 1, 0)     # 設置相機的"上"方向
        self.model_updated.emit()