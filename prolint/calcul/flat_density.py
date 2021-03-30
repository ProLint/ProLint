import numpy as np
from sys import getsizeof
import pickle


def flat_density(t, lipid, frames):

    if len(lipid) == 1:
        selection_string = "resname {}".format(lipid[0])
    else:

        s_st_list = ["{} or resname ".format(x) for x in lipid[:-1]]

        selection_string = "resname "
        for s in s_st_list:
            selection_string += s
        selection_string += lipid[-1]

    lipid_ndx = t.topology.select(selection_string)
    lipid_xyz = t.xyz[:, lipid_ndx, :]

    def slice_array(arr, slice_by):
        mask = np.ones_like(arr, dtype=bool)
        mask[::int(slice_by)] = False
        xshape = int(frames - mask[::int(slice_by)].shape[0])
        arr = arr[mask].reshape(xshape*arr.shape[1], 3)

        return arr

    lipid_xyz = lipid_xyz.reshape(lipid_xyz.shape[0]*lipid_xyz.shape[1], 3)

    array_memory_size = len(pickle.dumps(lipid_xyz)) / 1024
    while array_memory_size > 5000:
        # slice_by = int(frames / (frames * 0.1))
        # lipid_xyz = lipid_xyz[::20]

        # lipid_xyz_copy = lipid_xyz.copy()
        lipid_xyz = slice_array(lipid_xyz, 10)

        array_memory_size = len(pickle.dumps(lipid_xyz)) / 1024

    return lipid_xyz
