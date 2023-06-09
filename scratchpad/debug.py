# System imports
import sys
from pathlib import Path
import numpy as np
import json

# Logging
import logging

# Local imports
# Add the sub_functions directory to the Python module search path
sub_functions_path = Path(__file__).resolve().parent / '..'
print(sub_functions_path)
sys.path.append(str(sub_functions_path))

# Do not move import from here!
from helpers.visualisation import visualize_vertex_connections, visualize_3D_boundary
from sub_functions.data_structures import DataStructure, Mesh, CoilPart
from sub_functions.read_mesh import create_unique_noded_mesh
from sub_functions.parameterize_mesh import parameterize_mesh, get_boundary_loop_nodes
from sub_functions.refine_mesh import  refine_mesh_delegated as refine_mesh
from CoilGen import CoilGen


def debug1():
    print("Planar mesh")
    from sub_functions.build_planar_mesh import build_planar_mesh

    planar_height = 2.0
    planar_width = 3.0
    num_lateral_divisions = 4
    num_longitudinal_divisions = 5
    rotation_vector_x = 1.0
    rotation_vector_y = 0.0
    rotation_vector_z = 0.0
    rotation_angle = 0.0
    center_position_x = 0.0
    center_position_y = 0.0
    center_position_z = 0.0
    mesh = build_planar_mesh(planar_height, planar_width, num_lateral_divisions, num_longitudinal_divisions,
                             rotation_vector_x, rotation_vector_y, rotation_vector_z, rotation_angle,
                             center_position_x, center_position_y, center_position_z)

    # Create debug data
    planar_mesh = {'vertices': mesh.vertices.tolist(), 'faces' : mesh.faces.tolist(), 'normal' : mesh.normal.tolist()}
    with open('tests/test_data/planar_mesh.json', 'w') as file:
        json.dump(planar_mesh, file)

    mesh = Mesh(vertices=mesh.vertices, faces=mesh.faces)
    print (mesh.trimesh_obj.is_watertight)

    vertices = mesh.get_vertices()
    faces = mesh.get_faces()
    log.debug(" Vertices shape: %s", vertices.shape)
    vertex_counts = np.bincount(faces.flatten())
    print("vertex_counts: ", vertex_counts)

    visualize_vertex_connections(vertices, 800, 'images/debug1_planar_0.png')
    # mesh.display()


    coil_parts = [CoilPart(coil_mesh=mesh)]
    input_args = DataStructure(sf_source_file='none', iteration_num_mesh_refinement=1)
    coil_parts = refine_mesh(coil_parts, input_args)

    vertices2 = mesh.get_vertices()
    visualize_vertex_connections(vertices2, 800, 'images/debug1_planar_1.png')

    #input_params = DataStructure(surface_is_cylinder_flag=False, circular_diameter_factor=0.0)
    #result = parameterize_mesh(parts, input_params)

# Save a small bi-planar mesh to file
def debug1b():
    print("Bi-planar mesh")
    from sub_functions.build_biplanar_mesh import build_biplanar_mesh

    planar_height = 2.0
    planar_width = 3.0
    num_lateral_divisions = 4
    num_longitudinal_divisions = 5
    target_normal_x = 0.0
    target_normal_y = 0.0
    target_normal_z = 1.0
    center_position_x = 0.0
    center_position_y = 0.0
    center_position_z = 0.0
    plane_distance = 0.5

    mesh = build_biplanar_mesh(planar_height, planar_width, num_lateral_divisions, num_longitudinal_divisions,
                             target_normal_x, target_normal_y, target_normal_z,
                             center_position_x, center_position_y, center_position_z, plane_distance)

    # Create debug data
    planar_mesh = {'vertices': mesh.vertices.tolist(), 'faces' : mesh.faces.tolist(), 'normal' : mesh.normal.tolist()}
    with open('tests/test_data/biplanar_mesh.json', 'w') as file:
        json.dump(planar_mesh, file)


# A Planar mesh with a hole in the middle
def debug2():
    print("Planar mesh with hole")

    # Create small planar mesh with a hole
    # Define the mesh parameters
    x_min, x_max = -1.0, 1.0
    y_min, y_max = -1.0, 1.0
    hole_min, hole_max = -0.25, 0.25
    num_rows, num_cols = 8, 8

    # Calculate step sizes
    x_step = (x_max - x_min) / num_rows
    y_step = (y_max - y_min) / num_cols

    # Generate vertices
    vertices = []
    for i in range(num_rows + 1):
        for j in range(num_cols + 1):
            x = x_min + i * x_step
            y = y_min + j * y_step

            # Check if the vertex is inside the hole region
            # if hole_min <= x <= hole_max and hole_min <= y <= hole_max:
            #    continue  # Skip this vertex

            z = 0.0  # Z-coordinate is 0 for a planar mesh
            vertices.append([x, y, z])

    vertices = np.array(vertices)

    # Generate faces
    faces = []
    for i in range(num_rows):
        for j in range(num_cols):
            v1 = i * (num_cols + 1) + j
            v2 = v1 + 1
            v3 = v1 + num_cols + 2
            v4 = v1 + num_cols + 1

            # Check if any vertex is inside the hole region
            if (hole_min <= vertices[v1, 0] <= hole_max and hole_min <= vertices[v1, 1] <= hole_max) or \
                    (hole_min <= vertices[v2, 0] <= hole_max and hole_min <= vertices[v2, 1] <= hole_max) or \
                    (hole_min <= vertices[v3, 0] <= hole_max and hole_min <= vertices[v3, 1] <= hole_max) or \
                    (hole_min <= vertices[v4, 0] <= hole_max and hole_min <= vertices[v4, 1] <= hole_max):
                continue  # Skip this face

            faces.append([v3, v2, v1])
            faces.append([v4, v3, v1])

    faces = np.array(faces)
    # Print the vertices and faces arrays
    # print("Vertices:\n", vertices)
    # print("Faces:\n", faces)

    log.debug(" Original vertices shape: %s", vertices.shape)
    log.debug(" Original faces shape: %s", faces.shape)

    planar_mesh = DataStructure(vertices=vertices, faces=faces, normal=np.array([0,0,1]))

    mesh = create_unique_noded_mesh(planar_mesh)
    # mesh.display()
    # print (mesh.trimesh_obj.is_watertight)
    vertices = mesh.get_vertices()
    faces = mesh.get_faces()

    vertex_counts = np.bincount(faces.flatten())
    print("vertex_counts: ", vertex_counts)

    log.debug(" Vertices shape: %s", vertices.shape)
    log.debug(" Faces shape: %s", faces.shape)

    parts = [DataStructure(coil_mesh=mesh)]

    input_params = DataStructure(surface_is_cylinder_flag=True, circular_diameter_factor=1.0)
    coil_parts = parameterize_mesh(parts, input_params)
    mesh_part = coil_parts[0].coil_mesh
    visualize_vertex_connections(mesh_part.uv, 800, 'images/planar_hole_projected2.png')



# Planar mesh from a file
def debug3():
    arg_dict = {
        'coil_mesh_file': 'dental_gradient_ccs_single_low.stl',
        'iteration_num_mesh_refinement': 0,  # the number of refinements for the mesh;
        'field_shape_function': 'x',  # definition of the target field
        'debug': 0
    }
    x = CoilGen(log, arg_dict)

    mesh_part = x.coil_parts[0].coil_mesh
    # visualize_vertex_connections(mesh_part.uv, 800, 'images/dental_gradient_projected2.png')
    # mesh_part.display()
    # log.debug(" Target field: %s", x.target_field)
    # log.debug(" coil_parts[0].one_ring_list: %s", x.coil_parts[0].one_ring_list)


# Plain cylindrical mesh
def debug4():
    print("Cylindrical mesh")
    from sub_functions.build_cylinder_mesh import build_cylinder_mesh

    # planar_mesh_parameter_list
    cylinder_height = 0.5
    cylinder_radius = 0.25
    num_circular_divisions = 8
    num_longitudinal_divisions = 6
    rotation_vector_x = 0.0
    rotation_vector_y = 1.0
    rotation_vector_z = 0.0
    rotation_angle = np.pi/4.0 # 0.0

    # cylinder_mesh_parameter_list

    cylinder_mesh = build_cylinder_mesh(cylinder_height, cylinder_radius, num_circular_divisions,
                               num_longitudinal_divisions, rotation_vector_x, rotation_vector_y,
                               rotation_vector_z, rotation_angle)


    mesh = create_unique_noded_mesh(cylinder_mesh)
    log.debug(" Normal: %s", mesh.normal_rep)
    print (mesh.trimesh_obj.is_watertight)
    vertices = mesh.get_vertices()
    faces = mesh.get_faces()
    log.debug(" Vertices shape: %s", vertices.shape)

    # DEBUG
    mesh.display()

    from sub_functions.data_structures import DataStructure
    parts = [DataStructure(coil_mesh=mesh)]

    input_params = DataStructure(surface_is_cylinder_flag=True, circular_diameter_factor=1.0, debug=1)
    coil_parts = parameterize_mesh(parts, input_params)
    mesh_part = coil_parts[0].coil_mesh
    visualize_vertex_connections(mesh_part.uv, 800, 'images/cylinder_projected2.png')

# Test Mesh refinement
def debug5():
    # Test 1: Trivial case: A single face
    vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
    faces = np.array([[0, 1, 2]])
    mesh = Mesh(vertices=vertices, faces=faces)

    mesh.refine(inplace=True)

    new_vertices = mesh.get_vertices()
    new_faces = mesh.get_faces()

    log.debug(" New vertices: %s -> %s", new_vertices.shape, new_vertices)
    log.debug(" New faces: %s -> %s", new_faces.shape, new_faces)

    # mesh.display()
    coil_parts = [CoilPart(coil_mesh=mesh)]
    input_args = DataStructure(sf_source_file='none', iteration_num_mesh_refinement=1)
    coil_parts = refine_mesh(coil_parts, input_args)
    
    mesh = coil_parts[0].coil_mesh
    mesh.display()

    new_vertices = mesh.get_vertices()
    new_faces = mesh.get_faces()

    log.debug(" New vertices: %s -> %s", new_vertices.shape, new_vertices)
    log.debug(" New faces: %s -> %s", new_faces.shape, new_faces)

def debug6():
    # Load mesh
    from sub_functions.read_mesh import stlread_local
    output = stlread_local('Geometry_Data/cylinder_radius500mm_length1500mm.stl')
    log.debug(" cylinder_radius500mm_length1500mm: vertices: %s, faces: %s, normals: %s", np.shape(output.vertices), np.shape(output.faces), np.shape(output.normals) )


if __name__ == "__main__":
    # Set up logging
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    #debug1() # Planar mesh
    debug1b() # Planar mesh
    # debug2() # Planar mesh with a hole
    # debug3() # Planar mesh from file
    # debug4() # Cylindrical mesh
    # debug5() # Refine a simple 1 face mesh into four.
    # debug6() # Examine cylinder_radius500mm_length1500mm.stl
