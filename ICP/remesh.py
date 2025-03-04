

import open3d as o3d
import matplotlib.pyplot as plt
import numpy as np
class PointCloudReconstruction:
    def __init__(self, data):
        self.pcd = data
        self.mesh = None
        self.densities = None
    
    def estimate_normals(self, k=100):
        self.pcd.estimate_normals()
        self.pcd.orient_normals_consistent_tangent_plane(k)
    
    def poisson_reconstruction(self, depth=8):
        with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug):
            self.mesh, self.densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                self.pcd, depth=depth)
    
    def filter_low_density(self, quantile=0.032):
        densities = np.asarray(self.densities)
        vertices_to_remove = densities < np.quantile(densities, quantile)
        self.mesh.remove_vertices_by_mask(vertices_to_remove)
    
    def smooth_mesh(self, iterations=5):
        self.mesh = self.mesh.filter_smooth_simple(number_of_iterations=iterations)
    
    def compute_normals_and_color(self, color=[1, 0.706, 0]):
        self.mesh.compute_vertex_normals()
        self.mesh.paint_uniform_color(color)
    
    def save_mesh(self, filename="mesh.stl"):
        o3d.io.write_triangle_mesh(filename, self.mesh)
    
    def visualize(self):
        o3d.visualization.draw_geometries([self.mesh])


# reconstructor = PointCloudReconstruction('multiway_registration_all.pcd')
# reconstructor.estimate_normals()
# reconstructor.poisson_reconstruction(depth=8)
# reconstructor.filter_low_density(quantile=0.032)
# reconstructor.smooth_mesh(iterations=5)
# reconstructor.compute_normals_and_color(color=[1, 0.706, 0])
# reconstructor.save_mesh("mesh-90.stl")
# reconstructor.visualize()