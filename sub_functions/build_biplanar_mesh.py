# System
import numpy as np

# Logging
import logging

# Local imports
from sub_functions.calc_3d_rotation_matrix_by_vector import calc_3d_rotation_matrix_by_vector
from sub_functions.data_structures import DataStructure
from sub_functions.build_planar_mesh import simple_planar_mesh, apply_rotation_translation

log = logging.getLogger(__name__)

def build_biplanar_mesh(planar_height, planar_width,
                        num_lateral_divisions, num_longitudinal_divisions,
                        target_normal_x, target_normal_y, target_normal_z,
                        center_position_x, center_position_y, center_position_z,
                        plane_distance):
    """
    Create a biplanar regular mesh in any orientation.

    Parameters:
    - planar_height (float): Height of the planar mesh.
    - planar_width (float): Width of the planar mesh.
    - num_lateral_divisions (int): Number of divisions in the lateral direction.
    - num_longitudinal_divisions (int): Number of divisions in the longitudinal direction.
    - target_normal_x (float): X-component of the target normal vector.
    - target_normal_y (float): Y-component of the target normal vector.
    - target_normal_z (float): Z-component of the target normal vector.
    - center_position_x (float): X-coordinate of the center position.
    - center_position_y (float): Y-coordinate of the center position.
    - center_position_z (float): Z-coordinate of the center position.
    - plane_distance (float): Distance between the two planes.

    Returns:
    - biplanar_mesh (dict): Dictionary containing the mesh faces and vertices.
    """

    simple_vertices1, faces1 = simple_planar_mesh(planar_height, planar_width, num_lateral_divisions, num_longitudinal_divisions)
    log.debug(" simple_vertices1 shape: %s", simple_vertices1.shape)
    # Shift the vertices up
    simple_vertices1 += np.array([0.0, 0.0, plane_distance/2.0])

    simple_vertices2, faces2 = simple_planar_mesh(planar_height, planar_width, num_lateral_divisions, num_longitudinal_divisions)
    log.debug(" simple_vertices2 shape: %s", simple_vertices2.shape)
    # Shift the vertices down
    simple_vertices2 -= np.array([0.0, 0.0, plane_distance/2.0])

    # Combine the vertix arrays
    simple_vertices = np.append(simple_vertices1, simple_vertices2, axis=0)
    log.debug(" simple_vertices shape: %s", simple_vertices.shape)

    log.debug(" faces1 shape: %s", faces1.shape)
    num_faces1 = simple_vertices1.shape[0]
    faces = np.append(faces1, faces2 + num_faces1, axis=0)

    # Translate and shift
    shifted_vertices, normal_rep = translate_and_shift(simple_vertices,
                                           target_normal_x, target_normal_y, target_normal_z,
                                           center_position_x, center_position_y, center_position_z)

    return DataStructure(vertices=shifted_vertices, faces=faces, normal=normal_rep)


def translate_and_shift(vertices, 
                        target_normal_x, target_normal_y, target_normal_z,
                        center_position_x, center_position_y, center_position_z):
    old_normal = np.array([0, 0, 1])
    target_normal = np.array([target_normal_x, target_normal_y, target_normal_z])
    
    if np.linalg.norm(np.cross(old_normal, target_normal)) != 0:
        rot_vec = np.cross(old_normal, target_normal) / np.linalg.norm(np.cross(old_normal, target_normal))
        rot_angle = np.arcsin(np.linalg.norm(np.cross(old_normal, target_normal)) / (np.linalg.norm(old_normal) * np.linalg.norm(target_normal)))
    else:
        rot_vec = np.array([0, 0, 1])
        rot_angle = 0
    
    # Rotate
    rot_mat = calc_3d_rotation_matrix_by_vector(rot_vec, rot_angle)    
    rot_vertices = np.dot(vertices, rot_mat)

    # Calculate representative normal
    normal = np.array([0.0, 0.0, 1.0])
    normal_rep = np.dot(normal, rot_mat)

    # Shift
    shifted_vertices = rot_vertices + np.array([center_position_x, center_position_y, center_position_z])

    return shifted_vertices, normal_rep
    

if __name__ == "__main__":
    # Set up logging
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    planar_height = 2.0
    planar_width = 3.0
    num_lateral_divisions = 4
    num_longitudinal_divisions = 4
    target_normal_x = 1.0
    target_normal_y = 0.0
    target_normal_z = 0.0
    center_position_x = 0.0
    center_position_y = 0.0
    center_position_z = 0.0
    plane_distance = 0.5
    mesh = build_biplanar_mesh(planar_height, planar_width,
                               num_lateral_divisions, num_longitudinal_divisions,
                               target_normal_x, target_normal_y, target_normal_z,
                               center_position_x, center_position_y, center_position_z,
                               plane_distance)
    print(mesh.vertices)
    print(mesh.faces)

"""
[[ 2.5000000e-01 -1.5000000e+00  1.0000000e+00]
 [ 2.5000000e-01 -7.5000000e-01  1.0000000e+00]
 [ 2.5000000e-01  0.0000000e+00  1.0000000e+00]
 [ 2.5000000e-01  7.5000000e-01  1.0000000e+00]
 [ 2.5000000e-01  1.5000000e+00  1.0000000e+00]
 [ 2.5000000e-01 -1.5000000e+00  5.0000000e-01]
 [ 2.5000000e-01 -7.5000000e-01  5.0000000e-01]
 [ 2.5000000e-01  0.0000000e+00  5.0000000e-01]
 [ 2.5000000e-01  7.5000000e-01  5.0000000e-01]
 [ 2.5000000e-01  1.5000000e+00  5.0000000e-01]
 [ 2.5000000e-01 -1.5000000e+00  1.5308085e-17]
 [ 2.5000000e-01 -7.5000000e-01  1.5308085e-17]
 [ 2.5000000e-01  0.0000000e+00  1.5308085e-17]
 [ 2.5000000e-01  7.5000000e-01  1.5308085e-17]
 [ 2.5000000e-01  1.5000000e+00  1.5308085e-17]
 [ 2.5000000e-01 -1.5000000e+00 -5.0000000e-01]
 [ 2.5000000e-01 -7.5000000e-01 -5.0000000e-01]
 [ 2.5000000e-01  0.0000000e+00 -5.0000000e-01]
 [ 2.5000000e-01  7.5000000e-01 -5.0000000e-01]
 [ 2.5000000e-01  1.5000000e+00 -5.0000000e-01]
 [ 2.5000000e-01 -1.5000000e+00 -1.0000000e+00]
 [ 2.5000000e-01 -7.5000000e-01 -1.0000000e+00]
 [ 2.5000000e-01  0.0000000e+00 -1.0000000e+00]
 [ 2.5000000e-01  7.5000000e-01 -1.0000000e+00]
 [ 2.5000000e-01  1.5000000e+00 -1.0000000e+00]
 [-2.5000000e-01 -1.5000000e+00  1.0000000e+00]
 [-2.5000000e-01 -7.5000000e-01  1.0000000e+00]
 [-2.5000000e-01  0.0000000e+00  1.0000000e+00]
 [-2.5000000e-01  7.5000000e-01  1.0000000e+00]
 [-2.5000000e-01  1.5000000e+00  1.0000000e+00]
 [-2.5000000e-01 -1.5000000e+00  5.0000000e-01]
 [-2.5000000e-01 -7.5000000e-01  5.0000000e-01]
 [-2.5000000e-01  0.0000000e+00  5.0000000e-01]
 [-2.5000000e-01  7.5000000e-01  5.0000000e-01]
 [-2.5000000e-01  1.5000000e+00  5.0000000e-01]
 [-2.5000000e-01 -1.5000000e+00 -1.5308085e-17]
 [-2.5000000e-01 -7.5000000e-01 -1.5308085e-17]
 [-2.5000000e-01  0.0000000e+00 -1.5308085e-17]
 [-2.5000000e-01  7.5000000e-01 -1.5308085e-17]
 [-2.5000000e-01  1.5000000e+00 -1.5308085e-17]
 [-2.5000000e-01 -1.5000000e+00 -5.0000000e-01]
 [-2.5000000e-01 -7.5000000e-01 -5.0000000e-01]
 [-2.5000000e-01  0.0000000e+00 -5.0000000e-01]
 [-2.5000000e-01  7.5000000e-01 -5.0000000e-01]
 [-2.5000000e-01  1.5000000e+00 -5.0000000e-01]
 [-2.5000000e-01 -1.5000000e+00 -1.0000000e+00]
 [-2.5000000e-01 -7.5000000e-01 -1.0000000e+00]
 [-2.5000000e-01  0.0000000e+00 -1.0000000e+00]
 [-2.5000000e-01  7.5000000e-01 -1.0000000e+00]
 [-2.5000000e-01  1.5000000e+00 -1.0000000e+00]]
[[ 1  2 -3]
 [ 6  7  2]
 [11 12  7]
 [16 17 12]
 [ 2  3 -2]
 [ 7  8  3]
 [12 13  8]
 [17 18 13]
 [ 3  4 -1]
 [ 8  9  4]
 [13 14  9]
 [18 19 14]
 [ 4  5  0]
 [ 9 10  5]
 [14 15 10]
 [19 20 15]
 [ 1  1  2]
 [ 6  6  7]
 [11 11 12]
 [16 16 17]
 [ 2  2  3]
 [ 7  7  8]
 [12 12 13]
 [17 17 18]
 [ 3  3  4]
 [ 8  8  9]
 [13 13 14]
 [18 18 19]
 [ 4  4  5]
 [ 9  9 10]
 [14 14 15]
 [19 19 20]
 [26 27 22]
 [31 32 27]
 [36 37 32]
 [41 42 37]
 [27 28 23]
 [32 33 28]
 [37 38 33]
 [42 43 38]
 [28 29 24]
 [33 34 29]
 [38 39 34]
 [43 44 39]
 [29 30 25]
 [34 35 30]
 [39 40 35]
 [44 45 40]
 [26 26 27]
 [31 31 32]
 [36 36 37]
 [41 41 42]
 [27 27 28]
 [32 32 33]
 [37 37 38]
 [42 42 43]
 [28 28 29]
 [33 33 34]
 [38 38 39]
 [43 43 44]
 [29 29 30]
 [34 34 35]
 [39 39 40]
 [44 44 45]]
"""
