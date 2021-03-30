import numpy as np
import mdtraj as md

def shift_range(values):
    """
    Shift values from one range to another.
    """
    old_min = min(values)
    old_max = max(values)
    new_min = 0
    new_max = 99

    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    new_val = []
    for val in values:
        try:
            new_value = (((val - old_min) * new_range) / old_range) + new_min
        except ZeroDivisionError:
            new_value = new_min
        new_val.append(new_value)
    return new_val


def calculate_bfactor(slided_dframe, column):
    """
    Given an input list/array, return an array with its range
    shifted to conform with bfactor column values in PDB files.
    """
    parameter = slided_dframe[column].to_list()
    bfactor = np.array(shift_range(parameter)).tolist()

    return list(bfactor)


def create_structure_file(file_path, resolution="martini"):
    """
    Create a new trajectory object to add bfactors to.
    """
    struc_file = md.load(file_path)

    if resolution == "martini":
        # get protein indices
        prot_ndx = struc_file.top.select("name BB or (name =~ 'SC[1-5]')")

        # DataFrame containing only protein atoms
        ccdf = struc_file.top.to_dataframe()[0].iloc[prot_ndx]

        # Get only BB atoms, reset index to perserve the
        # old index values of BB beads.
        ccdf = ccdf[ccdf.name == "BB"]
        ccdf = ccdf.reset_index()
    else:
        # get protein indices
        prot_ndx = struc_file.top.select("protein")

        # DataFrame containing only protein atoms
        ccdf = struc_file.top.to_dataframe()[0].iloc[prot_ndx]

        # Get only BB atoms, reset index to perserve the
        # old index values of BB beads.
        ccdf = ccdf[ccdf.name == "CA"]
        ccdf = ccdf.reset_index()


    # Use BB indices to create an atom slice list
    atom_indices = ccdf['index'].to_list()

    # Create a new MDTraj topology from the DataFrame.
    # Create a new trajectory object using atom_indices
    # new_pdb = md.Topology.from_dataframe(ccdf)
    new_struc_file = struc_file.atom_slice(atom_indices)

    return new_struc_file

def save_heatmap(lipid, radius, column, protein_df, number_of_repeats):

    # Calculate bfactor column
    sliced_dframe = protein_df[(protein_df.Lipids == lipid) &
                            (protein_df.Radius == radius)]

    # Each protein has the same contact heatmap. Ideally, they all
    # should be different, but doing that involves calculating two
    # DB maps: An average and one for all protein (or selecting 1 of them only)
    bfactor = calculate_bfactor(sliced_dframe, column)
    bfactor = np.concatenate([bfactor] * number_of_repeats)
    bfactor = list(bfactor)

    return bfactor
