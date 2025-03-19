from PyQt5.QtCore import  pyqtSignal
from .BaseModel import BaseModel
import os
from Otherfunction import readmodel,singleimgcolor,trianglegood,pictureedgblack,twopicturedege,combineABC
import vtk

class AipredictModel(BaseModel):
    model_updated = pyqtSignal()  # Define the signal at the class level
    
    def __init__(self):
        super().__init__()  # Make sure to call the superclass constructor
        self.model_folder = ""
        self.upper_file = ""
        self.lower_file = ""
        self.lower_actor = None
        self.upper_actor = None
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
        upimage_file_cleaned = self.upper_file.strip("' ").strip()

        base_name = os.path.splitext(os.path.basename(image_file_cleaned))[0]
        base_name_up = os.path.splitext(os.path.basename(upimage_file_cleaned))[0]
        renderer.ResetCamera()
        renderer.GetRenderWindow().Render()
        # self.model_updated.emit()
        renderer.GetRenderWindow().SetSize(256, 256)
        self.lower_file_modify = self.output_folder+"/"+base_name+"_modtify.ply"

        # TODO  need to judge up and down , if up yes build three picture else build one picture
        if self.lower_file and  self.output_folder and  self.model_folder and self.upper_file:
            self.upper_opacity = 0 
            self.upper_actor.GetProperty().SetOpacity(self.upper_opacity)
            # 這邊先打編輯後的深度圖
            output_file_path_down=self.combine_three_depth(renderer)
            self.upper_opacity = 1
            self.lower_opacity = 0
            self.upper_actor.GetProperty().SetOpacity(self.upper_opacity)
            self.lower_actor.GetProperty().SetOpacity(self.lower_opacity)
            output_file_path_up=self.combine_three_depth(renderer)
            pictureedgblack.mark_boundary_points(output_file_path_up,self.output_folder+"/edgeUp", color=(255, 255, 0))
            pictureedgblack.mark_boundary_points(output_file_path_down,self.output_folder+"/edgeDown")
            twopicturedege.combine_image(self.output_folder+"/edgeDown/"+base_name+"down"
                                         , self.output_folder+"/edgeUp/"+base_name_up
                                         , self.output_folder+"/combinetwoedge/"
                                         ,output_file_path_down
                                         ,output_file_path_up)
            predictthree_pic=self.output_folder+"/predict.png"
            combineABC.merge_images(output_file_path_down,output_file_path_up,self.output_folder+"/combinetwoedge/"+base_name+".png",predictthree_pic)
            output_file_path_ai = self.output_folder+'/ai_'+base_name+".png"
            # 再用gan產生ai的深度
            singleimgcolor.apply_gan_model(self.model_folder, predictthree_pic, output_file_path_ai)
            # reference_ply = "D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/alldata_down"+f"/{base_name}.ply"
            output_stl_path = self.output_folder+'/ai_'+base_name+".stl"
            self.upper_opacity = 0
            self.lower_opacity = 1
            self.upper_actor.GetProperty().SetOpacity(self.upper_opacity)
            self.lower_actor.GetProperty().SetOpacity(self.lower_opacity)
            # 再用重建產生ai的深度
            reconstructor =trianglegood.DentalModelReconstructor(output_file_path_ai,self.lower_file,output_stl_path)
            reconstructor.reconstruct()
            smoothed_stl_path = self.output_folder + '/ai_' + base_name + "_smooth.stl"
            self.smooth_stl(output_stl_path, smoothed_stl_path)
            readmodel.render_file_in_second_window(render2,smoothed_stl_path)
        elif self.lower_file and  self.output_folder and self.model_folder:
            self.upper_opacity = 0 
            # 這邊先打編輯後的深度圖
            output_file_path=self.save_depth_map(renderer)
            output_file_path_ai = self.output_folder+'/ai_'+base_name+".png"
            # 再用gan產生ai的深度
            singleimgcolor.apply_gan_model(self.model_folder, output_file_path, output_file_path_ai)
            # reference_ply = "D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/alldata_down"+f"/{base_name}.ply"
            output_stl_path = self.output_folder+'/ai_'+base_name+".stl"
            self.SaveCurrentRenderWindowAsPLY(renderer,self.lower_file_modify)
            # 再用重建產生ai的深度
            reconstructor =trianglegood.DentalModelReconstructor(output_file_path_ai,self.lower_file_modify,output_stl_path)
            reconstructor.reconstruct()
            smoothed_stl_path = self.output_folder + '/ai_' + base_name + "_smooth.stl"
            self.smooth_stl(output_stl_path, smoothed_stl_path)
            
            readmodel.render_file_in_second_window(render2,smoothed_stl_path)
        self.model_updated.emit()
        renderer.GetRenderWindow().SetSize(768, 768)
        
        return True

    def smooth_stl(self, input_stl_path, output_stl_path, iterations=20, relaxation_factor=0.2):
        """對 STL 進行平滑處理"""
        reader = vtk.vtkSTLReader()
        reader.SetFileName(input_stl_path)
        
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInputConnection(reader.GetOutputPort())
        smoother.SetNumberOfIterations(iterations)  # 設定平滑迭代次數
        smoother.SetRelaxationFactor(relaxation_factor)  # 控制平滑強度
        smoother.FeatureEdgeSmoothingOff()
        smoother.BoundarySmoothingOn()
        smoother.Update()

        writer = vtk.vtkSTLWriter()
        writer.SetFileName(output_stl_path)
        writer.SetInputConnection(smoother.GetOutputPort())
        writer.Write()

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
