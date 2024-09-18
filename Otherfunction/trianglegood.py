import numpy as np
from PIL import Image
from stl import mesh
from .plybb import get_bounding_box, read_ply, get_depth_from_gray_value

def process_image(image_path):
    image = Image.open(image_path).convert('L')
    width, height = image.size
    return image, width, height

def find_image_bounds(image, width, height):
    max_value, min_value = 0, 255
    max_x_value, min_x_value = 0, width
    max_y_value, min_y_value = 0, height


    for y in range(height):
        for x in range(width):
            pixel_value = image.getpixel((x, y))
            max_value = max(max_value, pixel_value)
            min_value = min(min_value, pixel_value)
            if pixel_value != 0:
                min_x_value = min(min_x_value, x)
                max_x_value = max(max_x_value, x)
                min_y_value = min(min_y_value, y)
                max_y_value = max(max_y_value, y)
    return max_value, min_value, max_x_value, min_x_value, min_y_value, max_y_value

def generate_points(image, n, max_value, min_value, max_x_value, min_x_value, min_x, max_x, min_y, max_y, min_z, max_z):
    txtpoint = np.empty((0, 3), dtype=float)
    remesh_bounds = {'x': [None, None], 'y': [None, None], 'z': [None, None]}

    for y in range(n-1, -1, -1):
        for x in range(n-1, -1, -1):
            gray_value = image.getpixel((x, 255-y))
            new_x = get_depth_from_gray_value(x, max_x_value, min_x_value, min_x, max_x)
            new_y = get_depth_from_gray_value(y, 255, 0, min_y, max_y)
            new_z = get_depth_from_gray_value(gray_value, max_value, min_value, min_z, max_z)

            update_remesh_bounds(remesh_bounds, x, y, gray_value, new_x, new_y, new_z, min_x_value, max_x_value, min_value, max_value)

            txtpoint = np.append(txtpoint, [[new_x, new_y, new_z]], axis=0)

    return txtpoint, remesh_bounds

def update_remesh_bounds(bounds, x, y, gray_value, new_x, new_y, new_z, min_x_value, max_x_value, min_value, max_value):
    if x == min_x_value:
        bounds['x'][0] = new_x
    if x == max_x_value:
        bounds['x'][1] = new_x
    if y == 0:
        bounds['y'][0] = new_y
    if y == 255:
        bounds['y'][1] = new_y
    if gray_value == min_value:
        bounds['z'][0] = new_z
    if gray_value == max_value:
        bounds['z'][1] = new_z

def generate_vertices(txtpoint, n, final_end):
    vertices = []
    for column in range(0, final_end, n):
        for level in range(n-1):
            vertices.extend([
                [txtpoint[column + level], txtpoint[column + level + 1], txtpoint[column + level + n]],
                [txtpoint[column + level + 1], txtpoint[column + level + n], txtpoint[column + level + n + 1]]
            ])
    return vertices

def filter_vertices(vertices, remesh_bounds):
    min_z_depth = np.min([point[2] for triangle in vertices for point in triangle])
    return [
        triangle for triangle in vertices
        if not (
            all(point[2] == min_z_depth for point in triangle) or
            any(point[0] < remesh_bounds['x'][0] or point[0] > remesh_bounds['x'][1] for point in triangle) or
            any(point[1] < remesh_bounds['y'][0] or point[1] > remesh_bounds['y'][1] for point in triangle)
        )
    ]

def create_mesh(vertices, stl_path):
    mesh_3d = mesh.Mesh(np.zeros(len(vertices), dtype=mesh.Mesh.dtype))
    for i, triangle in enumerate(vertices):
        for j, point in enumerate(triangle):
            mesh_3d.vectors[i][j] = point
    mesh_3d.save(stl_path)


def process_image_to_stl(image_path, stl_path, ply_file, n=256):
    """
    Converts an image to an STL mesh file by processing the image and generating vertices and mesh.
    
    Args:
        image_path (str): Path to the input image.
        stl_path (str): Path to save the output STL file.
        ply_file (str): Path to the PLY file to extract vertex data.
        n (int): The resolution or size factor for point generation and meshing. Default is 256.
    
    Returns:
        None
    """
    # Read vertices from the PLY file
    vertices = read_ply(ply_file)
    
    # Get the bounding box for the vertices
    min_x, max_x, min_y, max_y, min_z, max_z = get_bounding_box(vertices)
    
    # Process the image and get its width and height
    image, width, height = process_image(image_path)
    
    # Find image bounds (min/max pixel values and positions)
    max_value, min_value, max_x_value, min_x_value, max_y_value, min_y_value = find_image_bounds(image, width, height)
    
    # Calculate the final end value based on the resolution
    final_end = n * (n-1)
    
    # Generate points based on the image and bounds
    txtpoint, remesh_bounds = generate_points(image, n, max_value, min_value, max_x_value, min_x_value, min_x, max_x, min_y, max_y, min_z, max_z)
    
    # Generate vertices based on the generated points
    vertices = generate_vertices(txtpoint, n, final_end)
    
    # Filter vertices based on the remesh bounds
    new_vertices = filter_vertices(vertices, remesh_bounds)
    
    # Create the STL mesh and save it to the specified path
    create_mesh(new_vertices, stl_path)

# process_image_to_stl('./data0002.png', './data0002.stl', './data0002.ply')