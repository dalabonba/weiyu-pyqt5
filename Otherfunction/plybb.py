#plybb.py

import numpy as np
from plyfile import PlyData



def get_bounding_box(vertices):
     """
     計算3D模型的邊界框
    
     參數:
     vertices (numpy.array): 3D模型的頂點座標，每行一個頂點，每列一個座標（x、y、z）
    
     返回:
     (min_x, max_x, min_y, max_y, min_z, max_z) (tuple): 邊界框的座標範圍
     """
     min_x = np.min(vertices[:, 0])
     max_x = np.max(vertices[:, 0])
     min_y = np.min(vertices[:, 1])
     max_y = np.max(vertices[:, 1])
     min_z = np.min(vertices[:, 2])
     max_z = np.max(vertices[:, 2])
    
     return min_x, max_x, min_y, max_y, min_z, max_z


def read_ply(file_path):
     """
     讀取PLY文件，並返回頂點座標
    
     參數:
     file_path (str): PLY檔案路徑
    
     返回:
     vertices (numpy.array): 頂點座標，每行一個頂點，每列一個座標（x、y、z）
     """
     ply_data = PlyData.read(file_path)
     vertices = np.vstack([ply_data['vertex']['x'],
                           ply_data['vertex']['y'],
                           ply_data['vertex']['z']]).T
     return vertices


def get_depth_from_gray_value(gray_value,depth_max,depth_min, min_z, max_z):
  """
  根據影像灰階值、最小深度值和最大深度值，計算深度值。

  引數：
    gray_value: 輸入值
    depth_max:圖片最大深度值
    depth_min:圖片最小深度值
    min_z: 最小的3維BB
    max_z: 最大的3維BB
  回傳值：
    深度值。
  """
  depthnum = (depth_max-depth_min) / (max_z - min_z)
  threednum = gray_value / depthnum
  z = threednum + min_z
  return z


def rotate_point_cloud(point_cloud, angle, axis='z'):
    """
    Rotate the point cloud along one of the axes
    Args:
        point_cloud: (np.array)
        angle: (float) angle of rotation in degrees
        axis: (str) 'x', 'y', or 'z'
    Returns:
        rotated_point_cloud: (np.array)
    """
    angle = angle * np.pi / 180.0  # convert to radians
    
    if axis == 'x':
        rotation_matrix = np.array([[1, 0, 0],
                                    [0, np.cos(angle), -np.sin(angle)],
                                    [0, np.sin(angle), np.cos(angle)]])
    elif axis == 'y':
        rotation_matrix = np.array([[np.cos(angle), 0, np.sin(angle)],
                                    [0, 1, 0],
                                    [-np.sin(angle), 0, np.cos(angle)]])
    else:  # axis == 'z'
        rotation_matrix = np.array([[np.cos(angle), -np.sin(angle), 0],
                                    [np.sin(angle), np.cos(angle), 0],
                                    [0, 0, 1]])

    rotated_point_cloud = np.dot(point_cloud, rotation_matrix.T)
    return rotated_point_cloud

def get_centroid(vertices):
    """
    Calculate the centroid of a 3D model.

    Parameters:
        vertices (numpy.array): 3D model vertices, each row is a vertex, each column is a coordinate (x, y, z)

    Returns:
        (centroid_x, centroid_y, centroid_z) (tuple): Centroid coordinates
    """
    centroid_x = np.mean(vertices[:, 0])
    centroid_y = np.mean(vertices[:, 1])
    centroid_z = np.mean(vertices[:, 2])

    return centroid_x, centroid_y, centroid_z

# # 範例用法
# if __name__ == "__main__":
#      # 讀取PLY文件
#      ply_file = "./data0004.ply" # 替換為你的PLY檔案路徑
#      vertices = read_ply(ply_file)
    
#      # 計算邊界框
#      min_x, max_x, min_y, max_y, min_z, max_z = get_bounding_box(vertices)
    
#      # 輸出邊界框座標範圍
#      print("Bounding Box:")
#      print("min_x:", min_x)
#      print("max_x:", max_x)
#      print("min_y:", min_y)
#      print("max_y:", max_y)
#      print("min_z:", min_z)
#      print("max_z:", max_z)