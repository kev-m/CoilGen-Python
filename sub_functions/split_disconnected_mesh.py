# System imports
import numpy as np
# Logging
import logging

# Local imports
from data_structures import DataStructure

log = logging.getLogger(__name__)


def split_disconnected_mesh(coil_mesh_in):
    """
    Split the mesh and the stream function if there are disconnected pieces, such as shielded gradients.

    Args:
        coil_mesh_in (Mesh): Input coil mesh object with attributes 'faces' and 'vertices'.

    Returns:
        coil_parts (list): List of coil parts, each containing a separate Mesh.

    """

    return coil_mesh_in.separate_into_get_parts()
