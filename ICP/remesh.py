import open3d as o3d
import numpy as np

class PointCloudReconstruction:
    def __init__(self, data):
        # 初始化點雲重建類，接收點雲數據
        self.pcd = data  # 儲存輸入的點雲數據
        self.mesh = None  # 初始化網格為空
        self.densities = None  # 初始化密度值為空
    
    def estimate_normals(self, k=100):
        # 估計點雲的法向量
        self.pcd.estimate_normals()  # 計算每個點的法向量
        self.pcd.orient_normals_consistent_tangent_plane(k)  # 使用k個鄰居調整法向量方向一致性
    
    def poisson_reconstruction(self, depth=8):
        # 使用Poisson表面重建算法從點雲生成網格
        with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug):  # 設置調試級別的上下文管理器
            self.mesh, self.densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                self.pcd, depth=depth)  # 執行Poisson重建，生成網格和密度值，depth控制重建細節
    
    def filter_low_density(self, quantile=0.032):
        # 過濾掉低密度區域的頂點
        densities = np.asarray(self.densities)  # 將密度值轉換為numpy陣列
        vertices_to_remove = densities < np.quantile(densities, quantile)  # 標記低於指定分位數的頂點
        self.mesh.remove_vertices_by_mask(vertices_to_remove)  # 移除標記的低密度頂點
    
    def smooth_mesh(self, iterations=5):
        # 平滑網格表面
        self.mesh = self.mesh.filter_smooth_simple(number_of_iterations=iterations)  # 使用簡單平滑濾波器，迭代指定次數
    
    def compute_normals_and_color(self, color=[1, 0.706, 0]):
        # 計算網格的頂點法向量並設置統一顏色
        self.mesh.compute_vertex_normals()  # 計算網格的頂點法向量
        self.mesh.paint_uniform_color(color)  # 為網格塗上指定的RGB顏色
    
    def save_mesh(self, filename="mesh.stl"):
        # 將網格保存為文件
        o3d.io.write_triangle_mesh(filename, self.mesh)  # 將網格寫入指定文件（預設為STL格式）
    
    def visualize(self):
        # 可視化網格
        o3d.visualization.draw_geometries([self.mesh])  # 使用Open3D顯示網格