import os
import numpy as np
import xmltodict
import trimesh
import open3d as o3d
from matplotlib import cm
import matplotlib.pyplot as plt


mdp_template = dict(
    tesselation = "yes",
    system = "bilayer",
    procedure = 1,
    clustering = 1,

    rcut_h = "2.20",
    rcut_t = "2.20",

    rcut_vll = 0.66,
    rcut_vlp = 0.66,
    rcut_vpp = 0.66,
    curvature = 3,
    geometry = 1,
    filter_type = 1,
    filter_width = 9,
    filter_shift = 0.01,
    filter_delta = 0.4,
    filter_opt = 0,
)
# lipids to use when calculating thickness & curvature
l_grp2_plasma = [
    "DAPC",
    "DAPE",
    "DUPE",
    "DAPS",
    "DUPS",
    "APC",
    "UPC",
    "DPSM",
    "DBSM",
    "DXSM",
    "DPG1",
    "DXG1",
    "DPG3",
    "DXG3",
    "PPC",
]

def gsurf_files(gsurf_dir, prot_name, frames, lipid_names, nop, ps, pe):
    """
    Generates gsurf parameter input file.
    """
    grp1, grp2 = [], []
    for l in lipid_names:
        if l in l_grp2_plasma:
            grp2.append(l)
        elif "CHOL" not in l.upper() and "CE" not in l.upper()[-2:] and "DG" not in l.upper()[-2:]:
            grp1.append(l)

    if len(grp2) == 0:
        ngrps = 1
    else:
        ngrps = 2

    if len(grp1) == 0:
        return None


    f = open(os.path.join(gsurf_dir, prot_name + '.mdp'), 'a')
    lgrp1 = open(os.path.join(gsurf_dir, 'l-grp1.dat'), 'a')
    lgrp2 = open(os.path.join(gsurf_dir, 'l-grp2.dat'), 'a')
    for p, v in mdp_template.items():
        if p.startswith("filter"):
            f.write("filter-" + p.split("_")[1] + " = " + str(v) + "\n")
        else:
            f.write(p + " = " + str(v) + "\n")

    # Write custom parameters
    f.write("frames = {} {} {}\n".format("1", frames, "1"))
    f.write("l-ngrps = {}\n".format(ngrps))
    f.write("l-grp1 = file\n")
    if len(grp2) != 0:
        f.write("l-grp2 = file\n")

    # Protein information
    f.write("p-grps = {}\n".format(nop))
    for i in range(nop):
        f.write("p-grp{} = {}\n".format(i+1, "P_" + str(i+1) + "A"))

    for i in range(nop):
        f.write("p{}-Calpha = BB {} {}\n".format(i+1, ps[i], pe[i]))

    f.write("enrich = {}\n".format(0))
    f.write("end\n")

    for p1 in grp1:
        lgrp1.write(p1 + "\n")
    for p2 in grp2:
        lgrp2.write(p2 + "\n")

    # close files
    f.close()
    lgrp1.close()
    lgrp2.close()

    return None


def generate_ply(jvx, upload_dir):
    """
    Generate 3D models and color the surfaces based on their
    physical properties.
    """
    # when gsurf fails, this will fail too.
    # therefore, this may be a very common error that'll be reported to the user.
    os.rename(jvx, 'outie.xml')
    file_path = r'outie.xml'
    with open(file_path) as fd:
        doc = xmltodict.parse(fd.read())

    geometries = doc['jvx-model']['geometries']['geometry']

    ## Get all the geometries
    ## NOTE: box_geometry is not yet used.
    box_geometry = geometries[-1]
    down_plane_geometry = geometries[-2]
    mid_plane_geometry = geometries[-3]
    top_plane_geometry = geometries[-4]
    lipid_centers_geometry = geometries[-5]
    protein_geometry = geometries[:len(geometries)-5]


    def surface_coloring(curvature, profile="viridis"):
        """
        Color input surface.
        """
        range_min = curvature.min()
        range_max = curvature.max()

        cmap = cm.ScalarMappable(
            norm = plt.Normalize(range_min, range_max),
            cmap = plt.get_cmap(profile)
        )

        curvature_coloring = cmap.to_rgba(curvature)
        normalized_curvature_coloring = curvature_coloring * 255
        for i, v in enumerate(normalized_curvature_coloring):
            for j in [0, 1, 2]:
                normalized_curvature_coloring[i, j] = int(v[j])

        return normalized_curvature_coloring

    def xml_string_to_float(string_array, ndim=3):
        floats_array = np.zeros((len(string_array), ndim))
        for i, string in enumerate(string_array):
            string_array_list = [float(s) for s in string.split()]
            for j, number in enumerate(string_array_list):
                floats_array[i, j] = number

        return floats_array


    # Create Surfaces
    all_plane_vertices_and_faces = {}
    mesh_file_names = {
        0: os.path.join(upload_dir, 'top_plane_curv'),
        1: os.path.join(upload_dir, 'mid_plane_curv'),
        2: os.path.join(upload_dir, 'down_plane_curv'),
        3: os.path.join(upload_dir, 'top_thickness'),
        4: os.path.join(upload_dir, 'full_thickness'),
        5: os.path.join(upload_dir, 'down_thickness')
    }

    for file_key, plane_geometry in enumerate([top_plane_geometry, mid_plane_geometry, down_plane_geometry]):
        plane_points = plane_geometry['pointSet']['points']['p']
        plane_faces  = plane_geometry['faceSet']['faces']['f']

        plane_vertices_and_faces = {}
        for plane_data, mesh_component in zip([(plane_points, 3), (plane_faces, 4)], ['vertices', 'faces']):
            plane_data_floats = xml_string_to_float(plane_data[0], plane_data[1])
            plane_vertices_and_faces[mesh_component] = plane_data_floats

        all_plane_vertices_and_faces[file_key] = plane_vertices_and_faces

        mesh = trimesh.Trimesh(
        vertices = plane_vertices_and_faces['vertices'],
        faces = plane_vertices_and_faces['faces'],
        process = False
        )

        mcurve = trimesh.curvature.discrete_mean_curvature_measure(mesh, mesh.vertices, 0.1)
        gcurve = trimesh.curvature.discrete_gaussian_curvature_measure(mesh, mesh.vertices, 0.1)
        cmax = np.percentile(gcurve, 95)
        gcurve[np.where(gcurve > cmax)] = cmax

        mesh_file_name = mesh_file_names[file_key]
        for curvature, file_name in zip([mcurve, gcurve], [mesh_file_name, mesh_file_name + "_g"]):
            mesh.visual.vertex_colors = surface_coloring(curvature)
            save_file_name = mesh.export(file_name + ".ply")


    top_vertices  = all_plane_vertices_and_faces[0]['vertices']
    mid_vertices  = all_plane_vertices_and_faces[1]['vertices']
    down_vertices = all_plane_vertices_and_faces[2]['vertices']

    top_thickness_values = top_vertices[:, -1] - mid_vertices[:, -1]
    down_thickness_values = mid_vertices[:, -1] - down_vertices[:, -1]
    full_thickness_values = top_vertices[:, -1] - down_vertices[:, -1]

    for file_key, thickness in enumerate([top_thickness_values, full_thickness_values, down_thickness_values]):
        mesh = trimesh.Trimesh(
            vertices = all_plane_vertices_and_faces[file_key]['vertices'],
            faces = all_plane_vertices_and_faces[file_key]['faces'],
            process = False
        )

        mesh.visual.vertex_colors = surface_coloring(thickness)
        save_file_name = mesh.export(mesh_file_names[file_key+3] + ".ply")


    # Create PoinClouds
    point_file_names = {
        0: os.path.join(upload_dir, 'prots.ply'),
        1: os.path.join(upload_dir, 'centers.ply'),
    }

    for file_key, points_geometry in enumerate([protein_geometry, lipid_centers_geometry]):

        if file_key == 0:
            points = np.concatenate([
                        np.array(
                            points_geometry[x]['pointSet']['points']['p']) for x in range(len(protein_geometry)
                        )])
        else:
            points = points_geometry['pointSet']['points']['p']

        points_floats_array = xml_string_to_float(points, 3)


        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(points_floats_array)
        o3d.io.write_point_cloud(point_file_names[file_key], point_cloud)

    return None
