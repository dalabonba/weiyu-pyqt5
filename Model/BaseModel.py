from PyQt5.QtCore import QObject
import os
from Otherfunction import readmodel, pictureedgblack, fillwhite  # 載入外部函式庫，用於讀取模型、處理圖片邊界與填充白色區域

class BaseModel(QObject):  # 繼承 QObject 以支援 Qt 訊號槽機制
    def __init__(self):
        super().__init__()  # 呼叫父類別初始化

    # 設定上顎模型資料夾
    def set_upper_folder(self, folder_path):
        self.upper_folder = folder_path  # 記錄資料夾路徑
        if os.path.isdir(folder_path):  # 確保提供的路徑是資料夾
            self.upper_files = self._get_files_in_folder(folder_path)  # 取得資料夾內的檔案清單
            self.model_updated.emit()  # 發送模型更新訊號，通知 UI 更新
            return True
        return False

    # 設定下顎模型資料夾
    def set_lower_folder(self, folder_path):
        self.lower_folder = folder_path
        if os.path.isdir(folder_path):
            self.lower_files = self._get_files_in_folder(folder_path)
            self.model_updated.emit()
            return True
        return False

    # 取得指定資料夾內的檔案清單
    def _get_files_in_folder(self, folder_path):
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # 設定模型旋轉角度
    def set_model_angle(self, angle):
        self.angle = angle  # 記錄旋轉角度
        if not hasattr(self, 'lower_actor'):  # 如果尚未載入下顎模型，則直接發送更新通知
            self.model_updated.emit()
            return
        
        # 若同時載入上下顎模型，則旋轉兩個模型
        if hasattr(self, 'upper_actor') and self.lower_actor:
            readmodel.rotate_actor(self.upper_actor, self.models_center, self.angle)
            readmodel.rotate_actor(self.lower_actor, self.models_center, self.angle)
        else:  # 只旋轉下顎模型
            self.lower_center = readmodel.calculate_center(self.lower_actor)
            readmodel.rotate_actor(self.lower_actor, self.lower_center, self.angle)
            self.lower_center = readmodel.calculate_center(self.lower_actor)  # 重新計算中心
        self.model_updated.emit()

    # 將模型渲染至畫面
    def render_model(self, renderer):
        renderer.RemoveAllViewProps()  # 清除所有現有物件

        # 若有設定上顎檔案則載入並渲染
        if hasattr(self, 'upper_file'):
            if self.upper_file != '':
                self.model1 = readmodel.load_3d_model(self.upper_file)
                self.upper_actor = readmodel.create_actor(self.model1, (0.98, 0.98, 0.92))  # 設定淺色材質
                self.upper_actor.GetProperty().SetSpecular(0.5)  # 增加高光
                self.upper_actor.GetProperty().SetSpecularPower(20)  # 讓光澤更集中
                self.upper_actor.GetProperty().SetDiffuse(0.6)  # 光線柔和散射
                self.upper_actor.GetProperty().SetAmbient(0.3)  # 提高環境光影響
                self.upper_actor.GetProperty().SetOpacity(self.upper_opacity)  # 設定透明度
                self.upper_center = readmodel.calculate_center(self.upper_actor)
                renderer.AddActor(self.upper_actor)

        # 若有設定下顎檔案則載入並渲染
        if  hasattr(self, 'lower_file'):
            if  self.lower_file:
                self.model2 = readmodel.load_3d_model(self.lower_file)
                self.lower_actor = readmodel.create_actor(self.model2, (0.98, 0.98, 0.92))
                self.lower_actor.GetProperty().SetOpacity(self.lower_opacity)
                self.lower_actor.GetProperty().SetSpecular(0.5)  # 增加高光
                self.lower_actor.GetProperty().SetSpecularPower(20)  # 讓光澤更集中
                self.lower_actor.GetProperty().SetDiffuse(0.6)  # 光線柔和散射
                self.lower_actor.GetProperty().SetAmbient(0.3)  # 提高環境光影響
                renderer.AddActor(self.lower_actor)

        # 若同時載入上、下顎模型，則計算模型中心點
        if  hasattr(self, 'lower_actor') and  hasattr(self, 'upper_actor'):
            self.models_center = readmodel.twomodel_bound(self.lower_actor.GetBounds(), self.upper_actor.GetBounds())

        renderer.ResetCamera()  # 重置相機視角
        renderer.GetRenderWindow().Render()  # 重新渲染畫面

    # 儲存深度圖
    def save_depth_map(self, renderer):
    # 設定渲染視窗的大小為 256x256 像素
        renderer.GetRenderWindow().SetSize(256, 256)
        
        # 檢查是否設定了 lower_actor 和 output_folder
        if self.lower_actor and self.output_folder:
            # 清理檔案名稱，去除多餘的空格或單引號
            upper_file_cleaned = self.lower_file.strip("' ").strip()
            
            # 從 upper_file_cleaned 中提取檔案的基本名稱（不包含副檔名）
            base_name = os.path.splitext(os.path.basename(upper_file_cleaned))[0]
            
            # 生成輸出的檔案路徑，將 output_folder 與基本名稱和 ".png" 副檔名結合
            output_file_path = self.output_folder + '/' + base_name + ".png"
            
            # 如果 upper_opacity 等於 0，處理上層物件的透明度並進行深度圖處理
            if self.upper_opacity == 0:
                if hasattr(self, 'upper_actor'):
                    # 設定上層物件的透明度為指定值
                    self.upper_actor.GetProperty().SetOpacity(self.upper_opacity)
                
                # 使用幫助函數設定基於 BB（有向邊界框）的相機
                scale_filter = readmodel.setup_camera(renderer, renderer.GetRenderWindow(),
                                                            None, self.lower_actor, self.upper_opacity, self.angle)
                
                # 儲存深度圖像到輸出的路徑
                readmodel.save_depth_image(output_file_path, scale_filter)
                
                # 獲取圖像邊界並進行處理，將邊界內的區域填充為白色
                bound = pictureedgblack.get_image_bound(output_file_path)
                fillwhite.process_image_pair(bound, output_file_path, output_file_path)
            
            # 如果 upper_opacity 等於 1，設定上下層物件的透明度並處理深度圖
            elif self.upper_opacity == 1:
                # 設定上層和下層物件的透明度
                self.upper_actor.GetProperty().SetOpacity(self.upper_opacity)
                self.lower_actor.GetProperty().SetOpacity(self.lower_opacity)
                
                # 設定相機，這次使用 upper_center 並處理透明度和角度
                scale_filter = readmodel.setup_camera(renderer, renderer.GetRenderWindow(),
                                                            self.upper_center, self.lower_actor, self.upper_opacity, self.angle)
                
                # 儲存深度圖像
                readmodel.save_depth_image(output_file_path, scale_filter)
            
            # 還原渲染視窗大小為 768x768 像素
            renderer.GetRenderWindow().SetSize(768, 768)
            
            # 返回儲存的深度圖像檔案路徑
            return output_file_path
        else:
            # 如果 output_folder 未設定，打印提示訊息
            print("Output folder not set")
        
        # 若未成功執行，返回 None
        return None


    # 儲存更多深度圖（處理上顎和下顎分開存檔）
    def combine_three_depth(self, renderer):
        renderer.GetRenderWindow().SetSize(256, 256)
        base_name = os.path.splitext(os.path.basename(self.upper_file.strip("' ").strip()))[0][:-2]

        if self.upper_opacity == 1:
            output_file_path = f"{self.output_folder}/{base_name}up.png"
            self.upper_center = readmodel.calculate_center(self.upper_actor)
            scale_filter = readmodel.setup_camera(renderer, renderer.GetRenderWindow(), self.upper_center, self.lower_actor, self.upper_opacity, self.angle)
        else:
            output_file_path = f"{self.output_folder}/{base_name}down.png"
            scale_filter = readmodel.setup_camera(renderer, renderer.GetRenderWindow(), None, self.lower_actor, self.upper_opacity, self.angle)

        readmodel.save_depth_image(output_file_path, scale_filter)
        bound = pictureedgblack.get_image_bound(output_file_path)
        fillwhite.process_image_pair(bound, output_file_path, output_file_path)
        return output_file_path

    # 設定輸出深度圖的儲存資料夾
    def set_output_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.output_folder = folder_path
            self.model_updated.emit()
            return True
        return False

    # 重置模型狀態
    def reset(self, renderer):
        self.upper_file = ""
        self.lower_file = ""
        self.upper_center = None
        self.lower_center = None
        self.models_center = None

        if hasattr(self, 'upper_actor'):
            del self.upper_actor
        if hasattr(self, 'lower_actor'):
            del self.lower_actor

        # 重置相機位置
        camera = renderer.GetActiveCamera()
        camera.SetPosition(0, 0, 1)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 1, 0)

        self.model_updated.emit()  # 發送更新通知
