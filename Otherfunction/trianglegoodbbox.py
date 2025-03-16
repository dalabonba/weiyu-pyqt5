

from .plybb import  get_depth_from_gray_value

from plyfile import PlyData
import numpy as np
from stl import mesh
from PIL import Image
import vtk
from scipy.spatial.transform import Rotation as R


class DentalModelReconstructor:
    def __init__(self, image_path, ply_path, stl_output_path):
        self.image_path = image_path
        self.ply_path = ply_path
        self.stl_output_path = stl_output_path
        self.image = None
        self.vertices = None
        self.bounds = None
        
    def preprocess_image(self):
        """增強圖像預處理，專門針對牙齒模型特徵"""
        # 讀取並轉換為灰階
        self.image = Image.open(self.image_path).convert('L')
        img_array = np.array(self.image)
        
        self.image = Image.fromarray(img_array)
    # @staticmethod
    def compute_obb_bounds(polydata):
        
         # 讀取 PLY 檔案
        # reader = vtk.vtkPLYReader()
        # reader.SetFileName(ply_path)
        # reader.Update()
        # polydata = reader.GetOutput()

        if polydata.GetNumberOfPoints() == 0:
            raise ValueError("PLY 檔案中無點資料！")

        # 計算 OBB
        obb_tree = vtk.vtkOBBTree()
        corner, max_vec, mid_vec, min_vec, size = [0.0]*3, [0.0]*3, [0.0]*3, [0.0]*3, [0.0]*3
        obb_tree.ComputeOBB(polydata, corner, max_vec, mid_vec, min_vec, size)

        # 計算每個點與基點的差距
        corner = np.array(corner)
        max_vec = np.array(max_vec)
        mid_vec = np.array(mid_vec)
        min_vec = np.array(min_vec)
        
        # 選擇一個基點 (selected_index)
        base_point = corner

        # 建立其餘三個正交點
        points = np.array([
            base_point,
            base_point + max_vec,
            base_point + mid_vec,
            base_point + min_vec
        ])

        # 計算每個點與基點的軸向差距
        min_values, max_values = base_point.copy(), base_point.copy()

        for point in points:
            diffs = np.abs(point - base_point)
            max_diff_index = np.argmax(diffs)
            if point[max_diff_index] > base_point[max_diff_index]:
                max_values[max_diff_index] = max(point[max_diff_index], max_values[max_diff_index])
            else: 
                min_values[max_diff_index] = min(point[max_diff_index], min_values[max_diff_index])
        
        return max_values[0],min_values[0],max_values[1],min_values[1],max_values[2],min_values[2]
    
    @staticmethod
    def compute_obb_aligned_bounds(polydata):
        """
        計算 OBB 的邊界並對齊到世界坐標軸。
        
        參數:
        polydata: vtkPolyData 對象，表示輸入的 3D 資料。

        返回:
        aligned_bounds: 對齊後的邊界框
        rotation_matrix: 用於對齊的旋轉矩陣
        obb_center: OBB 的中心點
        """
        # 檢查輸入資料是否有點
        if polydata.GetNumberOfPoints() == 0:
            raise ValueError("PLY 檔案中沒有點資料！")

        # 初始化 vtkOBBTree 物件以計算 OBB
        obb_tree = vtk.vtkOBBTree()
        corner, max_vec, mid_vec, min_vec, size = [0.0]*3, [0.0]*3, [0.0]*3, [0.0]*3, [0.0]*3
        obb_tree.ComputeOBB(polydata, corner, max_vec, mid_vec, min_vec, size)

        # 轉換為 NumPy 陣列
        corner = np.array(corner)
        max_vec = np.array(max_vec)
        mid_vec = np.array(mid_vec)
        min_vec = np.array(min_vec)

        # 計算 OBB 中心
        obb_center = corner + (max_vec + mid_vec + min_vec) / 2.0

        # (1) 計算旋轉矯正矩陣
        # OBB 的主軸方向 (V1, V2, V3)
        V1 = max_vec / np.linalg.norm(max_vec)  # 歸一化
        V2 = mid_vec / np.linalg.norm(mid_vec)
        V3 = min_vec / np.linalg.norm(min_vec)

        # 目標標準基向量
        E1 = np.array([1, 0, 0])
        E2 = np.array([0, 1, 0])
        E3 = np.array([0, 0, 1])

        # 當前基向量矩陣 A 和目標基向量矩陣 B
        A = np.column_stack((V1, V2, V3))  # OBB 的基向量矩陣
        B = np.column_stack((E1, E2, E3))  # 世界坐標軸基向量矩陣

        # 計算旋轉矩陣 R，使得 R * A = B
        # R = B * A^-1
        rotation_matrix = B @ np.linalg.inv(A)

        # (2) 應用旋轉到模型
        points = np.array(polydata.GetPoints().GetData())
        points = points - obb_center  # 平移到原點
        aligned_points = (rotation_matrix @ points.T).T  # 應用旋轉
        aligned_points = aligned_points + obb_center  # 平移回原始位置

        # 更新 polydata 的點
        new_points = vtk.vtkPoints()
        new_points.SetData(np_to_vtk(aligned_points))
        polydata.SetPoints(new_points)

        # (3) 可選：計算對齊後的 AABB
        aligned_bounds = polydata.GetBounds()  # 返回 (xmin, xmax, ymin, ymax, zmin, zmax)

        return aligned_bounds

            
    def generate_point_cloud(self, occlusal_view=True, rotate_negative_90=False):
        """
        生成點雲資料，可選擇是否進行旋轉。
        
        參數:
        - occlusal_view (bool): 是否使用咬合面視角，不旋轉。
        - rotate_negative_90 (bool): 是否沿Y軸逆時針旋轉90度。

        回傳:
        - np.array: 生成的點雲座標陣列
        """
        # 初始化與讀取
        vertices_list = []
        image = self.image
        width, height = image.size
        ply_data = PlyData.read(self.ply_path)

        # 讀取PLY頂點資料
        vertices = np.vstack([ply_data['vertex']['x'],
                            ply_data['vertex']['y'],
                            ply_data['vertex']['z']]).T

        # ======= 如果需要旋轉才進行以下步驟 ========
        if not occlusal_view:
            # 計算質心並移動至原點
            centroid = np.mean(vertices, axis=0)
            vertices -= centroid

            # 定義旋轉矩陣
            rotation_matrix = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]]) if rotate_negative_90 else \
                            np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])

            # 套用旋轉
            vertices = vertices @ rotation_matrix.T

            # 將點雲移回原位置
            vertices += centroid

        # ======= 計算點雲範圍 ========
        min_x, max_x = np.min(vertices[:, 0]), np.max(vertices[:, 0])
        min_y, max_y = np.min(vertices[:, 1]), np.max(vertices[:, 1])
        min_z, max_z = np.min(vertices[:, 2]), np.max(vertices[:, 2])

        # 如果不是咬合面視角，壓縮Z軸
        if not occlusal_view:
            min_z = max_z - (max_z - min_z) * 0.5

        # ======= 生成點雲 ========
        min_x_value, max_x_value = 255, 0
        max_value, min_value = 0, 255

        for y in reversed(range(height)):
            for x in reversed(range(width)):
                gray_value = image.getpixel((x, y))
                new_x = get_depth_from_gray_value(x, max_x_value, min_x_value, min_x, max_x)
                new_y = get_depth_from_gray_value(height - y - 1, 255, 0, min_y, max_y)
                new_z = get_depth_from_gray_value(gray_value, max_value, min_value, min_z, max_z)
                vertices_list.append([new_x, new_y, new_z])

        return np.array(vertices_list)
    

        
    def generate_mesh(self, points):
        """生成三角形網格，並反轉法向量方向"""
        height, width = int(np.sqrt(len(points))), int(np.sqrt(len(points)))
        faces = []
        
        for y in range(height - 1):
            for x in range(width - 1):
                # 計算頂點索引
                v0 = y * width + x
                v1 = v0 + 1
                v2 = (y + 1) * width + x
                v3 = v2 + 1
                
                # 計算對角線長度來決定三角形的分割方式
                d1 = np.linalg.norm(points[v0] - points[v3])
                d2 = np.linalg.norm(points[v1] - points[v2])
                
                # 選擇較短的對角線作為分割線，並反轉三角形頂點順序以顛倒法向量
                if d1 < d2:
                    faces.extend([[v0, v3, v1], [v0, v2, v3]])  # 順序反轉
                else:
                    faces.extend([[v0, v2, v1], [v1, v2, v3]])  # 順序反轉
                    
            # 移除多餘的網格
        min_z_depth = np.min([point[2] for point in points])
        new_faces = []
        for face in faces:
            # 提取頂點座標
            triangle_points = [points[idx] for idx in face]
            z_values = [point[2] for point in triangle_points]
            x_values = [point[0] for point in triangle_points]
            y_values = [point[1] for point in triangle_points]

            # 判斷是否應移除 (完全平坦或超出範圍的網格)
            skip_triangle = (
                sum(z == min_z_depth for z in z_values) == 3 or
                min(x_values) == max(x_values) or
                min(y_values) == max(y_values)
            )

            if not skip_triangle:
                new_faces.append(face)
        # 創建和保存STL網格，計算時保留反轉後的法向量
        mesh_data = mesh.Mesh(np.zeros(len(new_faces), dtype=mesh.Mesh.dtype))
        for i, face in enumerate(new_faces):
            for j in range(3):
                mesh_data.vectors[i][j] = points[face[j]]
            
            # 手動反轉法向量方向
            normal = np.cross(
                mesh_data.vectors[i][1] - mesh_data.vectors[i][0],
                mesh_data.vectors[i][2] - mesh_data.vectors[i][0]
            )
            mesh_data.normals[i] = -normal / np.linalg.norm(normal)  # 反轉法向量
            
        mesh_data.save(self.stl_output_path)
        
    def reconstruct(self):
        """執行完整的重建過程"""
        self.preprocess_image()
        points = self.generate_point_cloud(True,False)
        self.generate_mesh(points)

def np_to_vtk(np_array):
    """將 NumPy 陣列轉換為 VTK 格式"""
    vtk_array = vtk.vtkDoubleArray()
    vtk_array.SetNumberOfComponents(3)
    vtk_array.SetNumberOfTuples(np_array.shape[0])
    for i, point in enumerate(np_array):
        vtk_array.SetTuple3(i, point[0], point[1], point[2])
    return vtk_array
# # Define file paths
# image_path = './0001/data0001.png'
# ply_path = './0001/data0001.ply'
# stl_output_path = './0001/data0001bbox.stl'

# image = Image.open(image_path).convert('L')
# width, height = image.size

# for y in range(height):
#     for x in range(width):
#         pixel_value = image.getpixel((x, y))
#         max_value = max(max_value, pixel_value)
#         min_value = min(min_value, pixel_value)
#         if pixel_value != 0:
#             min_x_value = min(min_x_value, x)
#             max_x_value = max(max_x_value, x)
# # Create an instance of the DentalModelReconstructor
# reconstructor = DentalModelReconstructor(image_path, ply_path, stl_output_path)

# # Call the reconstruct method to process the image and generate the STL file
# reconstructor.reconstruct()