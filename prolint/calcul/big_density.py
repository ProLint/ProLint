import os
import numpy as np
from gridData import Grid

def file_size(filename):
    size = os.path.getsize(filename) / (1024*1000)
    return size

def coordinate_array(traj, lipid):
    """
    Function to calculate a numpy array for a selection of coordinates.
    """

    # TODO: use prolint code to get this.
    if len(lipid) == 1:
        selection_string = "resname {}".format(lipid[0])
    else:
        s_st_list = ["{} or resname ".format(x) for x in lipid[:-1]]
        selection_string = "resname "
        for s in s_st_list:
            selection_string += s
        selection_string += lipid[-1]

    lipid_ndx = traj.topology.select(selection_string)
    lipid_xyz = traj.xyz[:, lipid_ndx, :]

    # Reshape array.
    lipid_xyz = lipid_xyz.reshape(lipid_xyz.shape[0] * lipid_xyz.shape[1], 3)

    return lipid_xyz


def coordinate_histogram(lipid_xyz, xbin=160, ybin=160, zbin=160):
    """
    Call histogrammdd on the coordinate array.
    """
    histogram, edges = np.histogramdd(lipid_xyz, bins=(xbin, ybin, zbin))

    return histogram, edges


def get_density(lipid_xyz, ul_max, x):

    xbin, ybin, zbin = int(ul_max[0]*x), int(ul_max[1]*x), int(ul_max[2]*x)
    system_h, system_e = coordinate_histogram(lipid_xyz, xbin, ybin, zbin)

    histogram, edges = system_h, system_e

    grid = Grid(histogram, edges=[e * 10 for e in edges])

    return grid

def save_dx(t, l_n, l_i, upload_dir, task_id):

    ul_max = np.amax(t.unitcell_lengths, axis=0)

    lipid_xyz = coordinate_array(t, l_i)

    # change the number 15 below to increase/decrease
    # the size of calculated densities.
    x = 1
    add = 1
    once = True
    grid = get_density(lipid_xyz, ul_max, x)
    file_name = os.path.join(upload_dir, 'lipid_x' + str(x) + '.dx')
    grid.export(file_name)
    fz = file_size(file_name)
    while fz <= 15:
        try:
            os.remove(file_name)
        except FileNotFoundError:
            pass

        # increment x
        x += add
        file_name = os.path.join(upload_dir, 'lipid_x' + str(x) + '.dx')

        grid = get_density(lipid_xyz, ul_max, x)
        grid.export(file_name)

        fz = file_size(file_name)

        print (fz)

        if fz > 15 and once:
            os.remove(file_name)
            x -= 1
            add = 0.1
            once = False
            fz = 14

    file_rename = os.path.join(upload_dir, task_id + '_' + str(l_n) + '_final.dx')
    os.rename(file_name, file_rename)

    return None