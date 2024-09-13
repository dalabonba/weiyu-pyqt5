import vtk
import os

def load_3d_model(filename):
    _, extension = os.path.splitext(filename)
    extension = extension.lower()

    if extension == '.ply':
        reader = vtk.vtkPLYReader()
    elif extension == '.stl':
        reader = vtk.vtkSTLReader()
    elif extension == '.obj':
        reader = vtk.vtkOBJReader()
    else:
        raise ValueError(f"Unsupported file format: {extension}")

    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

def create_actor(polydata, color):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    return actor

def calculate_center (actor):
    bounds = actor.GetBounds()
    center = [
        (bounds[1] + bounds[0]) *0.5,
        (bounds[3] + bounds[2]) *0.5,
        (bounds[5] + bounds[4]) *0.5
    ]
    return center

def twomodel_bound(upper_bounds,lower_bounds):
    combined_bounds = [
        min(upper_bounds[0], lower_bounds[0]),  # x_min
        max(upper_bounds[1], lower_bounds[1]),  # x_max
        min(upper_bounds[2], lower_bounds[2]),  # y_min
        max(upper_bounds[3], lower_bounds[3]),  # y_max
        min(upper_bounds[4], lower_bounds[4]),  # z_min
        max(upper_bounds[5], lower_bounds[5])   # z_max
    ]
    return combined_bounds

def rotate_actor(actor, center, angle):
    transform = vtk.vtkTransform()
    transform.Translate(-center[0], -center[1], -center[2])
    transform.RotateY(angle)  # 绕Y轴旋转
    transform.RotateX(0)  # 绕Y轴旋转
    transform.RotateZ(0)  # 绕Y轴旋转

    transform.Translate(center[0], center[1], center[2])
    actor.SetUserTransform(transform)

