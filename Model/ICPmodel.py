from PyQt5.QtCore import  pyqtSignal
from .BaseModel import BaseModel
import os
from Otherfunction import readmodel
from ICP import main
class ICPModel(BaseModel):
    model_updated = pyqtSignal()  # Define the signal at the class level
    
    def __init__(self):
        super().__init__()  # Make sure to call the superclass constructor
        self.front_file = ""
        self.left_file = ""
        self.right_file = ""
        self.output_folder = ""



    def set_reference_file(self, file_path,position_type):
        if os.path.exists(file_path):
            if position_type == "front":
                self.front_file = file_path
            elif position_type == "left":
                self.left_file = file_path
            elif position_type == "right":
                self.right_file = file_path
            self.model_updated.emit()
            return True
        return False
    
    def save_icp_file(self,renderer,render2):
        renderer.ResetCamera()
        renderer.GetRenderWindow().Render()
        self.model_updated.emit()
        icp_stl=main.process_and_reconstruct(self.front_file,self.left_file,self.right_file,self.output_folder)
        readmodel.render_file_in_second_window(render2,icp_stl)

        renderer.GetRenderWindow().SetSize(768, 768)
        
        return True
    def render_model_icp(self,renderer):
        renderer.RemoveAllViewProps() 
        if hasattr(self, 'front_file'):
                if self.front_file != '':
                    self.model1 = readmodel.load_3d_model(self.front_file)
                    self.front_actor = readmodel.create_actor(self.model1, (0.98, 0.98, 0.92)) 
                    self.front_actor.GetProperty().SetSpecular(0.5)  # 增加高光
                    self.front_actor.GetProperty().SetSpecularPower(20)  # 讓光澤更集中
                    self.front_actor.GetProperty().SetDiffuse(0.6)  # 光線柔和散射
                    self.front_actor.GetProperty().SetAmbient(0.3)  # 提高環境光影響
                    self.front_actor.GetProperty().SetOpacity(1)
                    self.upper_center = readmodel.calculate_center(self.front_actor)
                    renderer.AddActor(self.front_actor)
        if  self.left_file:
                self.model2 = readmodel.load_3d_model(self.left_file)
                # self.left_actor = readmodel.create_actor(self.model2, (0.95, 0.95, 0.88))  # 設為白色
                self.left_actor = readmodel.create_actor(self.model2, (0.98, 0.98, 0.92))  # 更明亮的白色
                self.left_actor.GetProperty().SetOpacity(1)
                self.left_actor.GetProperty().SetSpecular(0.5)  # 增加高光
                self.left_actor.GetProperty().SetSpecularPower(20)  # 讓光澤更集中
                self.left_actor.GetProperty().SetDiffuse(0.6)  # 光線柔和散射
                self.left_actor.GetProperty().SetAmbient(0.3)  # 提高環境光影響
                renderer.AddActor(self.left_actor)
        if  self.right_file:
                self.model3 = readmodel.load_3d_model(self.right_file)
                # self.right_actor = readmodel.create_actor(self.model2, (0.95, 0.95, 0.88))  # 設為白色
                self.right_actor = readmodel.create_actor(self.model3, (0.98, 0.98, 0.92))  # 更明亮的白色
                self.right_actor.GetProperty().SetOpacity(1)
                self.right_actor.GetProperty().SetSpecular(1.0)  # 增加高光
                self.right_actor.GetProperty().SetSpecularPower(20)  # 讓光澤更集中
                self.right_actor.GetProperty().SetDiffuse(0.6)  # 光線柔和散射
                self.right_actor.GetProperty().SetAmbient(0.3)  # 提高環境光影響
                renderer.AddActor(self.right_actor)
        renderer.ResetCamera()
        renderer.GetRenderWindow().Render()