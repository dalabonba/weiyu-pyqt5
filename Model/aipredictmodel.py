from PyQt5.QtCore import  pyqtSignal
from .BaseModel import BaseModel
import os
from Otherfunction import readmodel,singleimgcolor,trianglegood
import vtk

class AipredictModel(BaseModel):
    model_updated = pyqtSignal()  # Define the signal at the class level
    
    def __init__(self):
        super().__init__()  # Make sure to call the superclass constructor
        self.model_folder = ""
        self.upper_file = ""
        self.lower_file = ""
        self.upper_opacity = 1.0
        self.lower_opacity = 1.0
        self.output_folder = ""
        self.angle=0



    def set_reference_file(self, file_path,position_type):
        if os.path.exists(file_path):
            if position_type == "down":
                self.lower_file = file_path
            else:
                self.upper_file = file_path
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
        image_file_cleaned = self.lower_file.strip("' ").strip()
        base_name = os.path.splitext(os.path.basename(image_file_cleaned))[0]
        self.upper_opacity = 0.0
        renderer.ResetCamera()
        renderer.GetRenderWindow().Render()
        # self.model_updated.emit()
        renderer.GetRenderWindow().SetSize(256, 256)
        self.SaveCurrentRenderWindowAsPLY(renderer,self.output_folder+base_name+"_modtify.ply")
        self.lower_file = self.output_folder+base_name+"_modtify.ply"
        self.model_updated.emit()
        # TODO  need to judge up and down , if up yes build three picture else build one picture
        if self.lower_file and  self.output_folder and self.model_folder:
            # 這邊先打編輯後的深度圖
            output_file_path=self.save_depth_map(renderer)
            output_file_path_ai = self.output_folder+'/ai_'+base_name+".png"
            # 再用gan產生ai的深度
            singleimgcolor.apply_gan_model(self.model_folder, output_file_path, output_file_path_ai)
            # reference_ply = "D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/alldata_down"+f"/{base_name}.ply"
            output_stl_path = self.output_folder+'/ai_'+base_name+".stl"
            # 再用重建產生ai的深度
            reconstructor =trianglegood.DentalModelReconstructor(output_file_path_ai,self.lower_file,output_stl_path)
            reconstructor.reconstruct()
            readmodel.render_file_in_second_window(render2,output_stl_path)
        self.upper_opacity = 1.0
        # self.model_updated.emit()
        renderer.GetRenderWindow().SetSize(768, 768)
        
        return True


    def SaveCurrentRenderWindowAsPLY(self,renderer ,file_path):
        """
        Save the current visible model from the render window to a PLY file.
        This extracts all visible actors' polydata and merges them into a single file.
        """
        append_filter = vtk.vtkAppendPolyData()  # 用於合併多個 PolyData
        actor_count = 0

        # 遍歷目前場景中所有 Actor
        for actor in renderer.GetActors():
            mapper = actor.GetMapper()
            polydata = mapper.GetInput()
            if polydata:
                clean_filter = vtk.vtkCleanPolyData()  # 清理資料，移除重複點
                clean_filter.SetInputData(polydata)
                clean_filter.Update()
                append_filter.AddInputData(clean_filter.GetOutput())
                actor_count += 1

        if actor_count == 0:
            print("沒有可保存的模型。")
            return

        # 合併並保存
        append_filter.Update()
        ply_writer = vtk.vtkPLYWriter()
        ply_writer.SetFileName(file_path)
        ply_writer.SetInputData(append_filter.GetOutput())
        ply_writer.Write()
        print(f"已成功將當前場景模型保存為: {file_path}")
