import os
import json
import pickle
import shutil
import traceback
import numpy as np
import mdtraj as md
import pandas as pd
import prolintpy as pl
from pathlib import Path
from io import StringIO, BytesIO
from django.conf import settings
from celery import shared_task, Celery
from prolint.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, FROM_SENDER, EMAIL_CONFIGURED

app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@app.task
def calcul_contacts(traj_path, coor_path, username, task_id, upload_dir, user_inputs):
    """
    TODO: Add Docs!
    """
    OUTPUT_COLLECTION = StringIO()
    APPS_CALCULATED_SUCCESSFULLY = {
        'points': False,
        'line': False,
        'heatmap': False,
        'network': False,
        'thickcurv': False,
        'density': False,
        'radar': False
    }
    CALCULATED_CONTACTS = False
    ####################################################
    #################   User Inputs ####################
    ####################################################
    traj_path = os.path.join(upload_dir, traj_path)
    coor_path = os.path.join(upload_dir, coor_path)
    radii = user_inputs.get('radii')
    group_lipids = user_inputs.get('group_lipids')

    resolution = user_inputs.get('resolution')
    merge = user_inputs.get('chains')

    protein_names = user_inputs.get('proteins')
    if len(protein_names) == 1:
        prot_name = protein_names[0]
    else:
        prot_name = 'AllProteins'

    CALCULATIONS_REQUESTED = {
        'contacts': False,
        'densities': False,
        'thickcurv': False,
    }
    apps = user_inputs.get('apps')
    for app in ['contacts', 'densities', 'thickcurv']:
        if app in apps:
            CALCULATIONS_REQUESTED[app] = True

    ####################################################
    ########   MDTraj and ProLint definitions  #########
    ####################################################
    # Load the data into an mdtraj object
    t = md.load(traj_path, top=coor_path)
    frames = t.n_frames

    p = pl.Proteins(t.topology, resolution=resolution)
    proteins = p.system_proteins(merge=merge)
    if not merge:
        P = pl.Proteins(t.topology, resolution=resolution)
        first_protein = P.system_proteins(merge=True)[0]
        # first_protein = contacts_proteins
    else:
        first_protein = proteins[0]

    # protein names
    if len(protein_names) == len(proteins):
        for upx, user_pname in enumerate(protein_names):
            proteins[upx].name = user_pname

    # lipids
    if len(user_inputs.get('lipids')) == 0:
        lipids = pl.Lipids(t.topology, resolution=resolution)
        lipid_names = lipids.lipid_names().tolist()
    else:
        lipid_names = user_inputs.get('lipids')
        lipids = pl.Lipids(t.topology, resolution=resolution, lipid_names=lipid_names)

    if group_lipids and resolution == "martini":
        SYSTEM_LIPIDS = pl.martini_lipids(lipids.lipid_names())
    else:
        SYSTEM_LIPIDS = {}
        for lip in lipids.lipid_names():
            SYSTEM_LIPIDS[lip] = [lip]

    if group_lipids and resolution == "atomistic":
        group_lipids = False

    ####################################################
    ##############   Contact Analysis  #################
    ####################################################
    contacts = pl.ComputeContacts(t, proteins, lipids)

    if CALCULATIONS_REQUESTED['contacts']:
        try:
            n = contacts.compute_neighbors(t, cutoff=radii[0], grouped=group_lipids)
            protein_dataframe = pl.contacts_dataframe(n, proteins, t, radii[0], resolution)
            if len(radii) == 2:
                m = contacts.compute_neighbors(t, cutoff=radii[1], grouped=group_lipids)
                protein_dataframe = protein_dataframe.append(pl.contacts_dataframe(m, proteins, t, radii[1], resolution))

            protein_dataframe.to_csv(os.path.join(upload_dir, task_id + '.csv'), index=False)
            CALCULATED_CONTACTS = True
            OUTPUT_COLLECTION.write("Contact Analysis completed successfully.\n")
            APPS_CALCULATED_SUCCESSFULLY['points'] = True
            APPS_CALCULATED_SUCCESSFULLY['radar'] = True
        except Exception:
            CALCULATED_CONTACTS = False
            OUTPUT_COLLECTION.write('Contact Analysis returned the following error:\n#######################\n')
            OUTPUT_COLLECTION.write(traceback.format_exc())

            # ProLint depends on successfully calculated contacts.
            APPS_CALCULATED_SUCCESSFULLY['points'] = False
            APPS_CALCULATED_SUCCESSFULLY['radar'] = False
            APPS_CALCULATED_SUCCESSFULLY['density'] = False
            APPS_CALCULATED_SUCCESSFULLY['line'] = False
            APPS_CALCULATED_SUCCESSFULLY['network'] = False
            APPS_CALCULATED_SUCCESSFULLY['heatmap'] = False

    ####################################################
    #############   Distance Analysis  #################
    ####################################################
    # Depends on Contact Analysis
    if CALCULATIONS_REQUESTED['contacts']:
        if CALCULATED_CONTACTS:
            try:
                # if proteins were not merged, we need to undo that for this step:
                if not merge:
                    P = pl.Proteins(t.topology, resolution=resolution)
                    contacts_proteins = P.system_proteins(merge=True)[0]
                else:
                    contacts_proteins = proteins[0]

                distances_dict = {}
                # TODO: This does not take account of the radii, but should it?
                for protein in protein_dataframe.Protein.unique():
                    df = protein_dataframe[protein_dataframe.Protein == protein]
                    idx = df.Longest_Duration.sort_values(ascending=False)[:30].index
                    # df = df.iloc[idx]
                    df = df[df.index.isin(idx)]
                    lipids_found = df.Lipids.unique()
                    for lipid in lipids_found:
                        if group_lipids:
                            for group in SYSTEM_LIPIDS[lipid]:
                                distances_dict[group] = df[df.Lipids == lipid].ResID.to_list()
                        else:
                            distances_dict[lipid] = df[df.Lipids == lipid].ResID.to_list()

                if not merge:

                    distances = contacts.compute_lipid_distances(
                        t,
                        # proteins[0],
                        contacts_proteins,
                        distances_dict,
                        SYSTEM_LIPIDS,
                        lipids_found,
                        resolution,
                        p=P,
                        grouped=group_lipids
                        )
                else:
                    distances = contacts.compute_lipid_distances(
                        t,
                        proteins[0],
                        # contacts_proteins,
                        distances_dict,
                        SYSTEM_LIPIDS,
                        lipids_found,
                        resolution,
                        p=p,
                        grouped=group_lipids
                        )
                with open(os.path.join(upload_dir, 'distances' + '.p'), 'wb') as fp:
                    pickle.dump(distances, fp, protocol=pickle.HIGHEST_PROTOCOL)
                OUTPUT_COLLECTION.write('Distance Analysis completed successfully.\n')
                APPS_CALCULATED_SUCCESSFULLY['line'] = True
            except Exception:
                OUTPUT_COLLECTION.write('Distance Analysis returned the following error:\n#######################\n')
                OUTPUT_COLLECTION.write(traceback.format_exc())
                APPS_CALCULATED_SUCCESSFULLY['line'] = False

        else:
            OUTPUT_COLLECTION.write('Contact Analysis was unsuccessful. Skipping Distance Analysis as it depends on it.\n')

    ####################################################
    ###########   Membrane-Plane Density  ##############
    ####################################################
    if CALCULATIONS_REQUESTED['densities']:
        from .flat_density import flat_density
        try:
            # Save protein coordinates
            prot_xyz = t.xyz[0, p.p_indices, :]
            np.save(os.path.join(upload_dir, "prot_" + task_id + '.npy'), prot_xyz)

            # Save lipid coordinates
            for lg, li in SYSTEM_LIPIDS.items():
                l_xyz = flat_density(t, li, frames)
                np.save(os.path.join(upload_dir, str(lg) + "_" + task_id + '.npy'), l_xyz)
            OUTPUT_COLLECTION.write('Membrane-Plane Density completed successfully.\n')
            APPS_CALCULATED_SUCCESSFULLY['density'] = True
        except Exception:
            OUTPUT_COLLECTION.write('Membrane-Plane Density returned the following error:\n#######################\n')
            OUTPUT_COLLECTION.write(traceback.format_exc())
            APPS_CALCULATED_SUCCESSFULLY['density'] = False

    ####################################################
    ###############   Network Graph  ###################
    ####################################################
    if CALCULATIONS_REQUESTED['contacts']:
        if CALCULATED_CONTACTS:
            try:
                for r in radii:
                    for column in ['Mean_Duration', 'Longest_Duration', 'Sum_of_all_Contacts', 'Lipid_Number', 'Occupancy']:
                        collect_results = pl.network(
                            lipids,
                            protein_dataframe,
                            column,
                            grouped=group_lipids,
                            radius=r,
                            webserver=True
                            )
                        for result in collect_results:
                            graph_json, gpcr = result
                            file_name = os.path.join(upload_dir, gpcr + '__' + column + "__" + str(r) + '__network.json')
                            json.dump(graph_json, open(file_name, 'w'))

                OUTPUT_COLLECTION.write('Network Graph completed successfully.\n')
                APPS_CALCULATED_SUCCESSFULLY['network'] = True
            except Exception:
                OUTPUT_COLLECTION.write('Network Graph returned the following error:\n#######################\n')
                OUTPUT_COLLECTION.write(traceback.format_exc())
                APPS_CALCULATED_SUCCESSFULLY['network'] = False

        else:
            OUTPUT_COLLECTION.write('Contact Analysis was unsuccessful. Skipping Network Graph Analysis as it depends on it.\n')

    ####################################################
    #########   Density & Heatmap Analysis  ############
    ####################################################
    # Heatmap projections depend on Contact Analysis.
    from .pdb_bfactor import save_heatmap, create_structure_file
    if CALCULATIONS_REQUESTED['contacts'] & CALCULATIONS_REQUESTED['densities']:
        if CALCULATED_CONTACTS:
            try:
                df = protein_dataframe
                radii_list = df.Radius.unique().tolist()
                lipids_list = df.Lipids.unique().tolist()

                column_axis = {
                    'Sum_of_all_Contacts': "Sum of Contacts",
                    'Longest_Duration': "Longest Contact",
                    'Mean_Duration': 'Average Contacts',
                    'Lipid_Number': 'Nr. Lipids per Residue',
                    'Occupancy': 'Occupancy',
                }
                json_data = {}
                for r in radii_list:
                    for l in lipids_list:
                        for column in ['Sum_of_all_Contacts', 'Longest_Duration', 'Mean_Duration', 'Lipid_Number', 'Occupancy']:
                            if merge:
                                bfactor = save_heatmap(l, r, column, df, proteins[0].counter)
                                json_data[f'{r}_{l}_{column_axis[column]}'] = list(bfactor)
                            else:
                                bfactor = save_heatmap(l, r, column, df, first_protein.counter)
                                json_data[f'{r}_{l}_{column_axis[column]}'] = list(bfactor)

                # save json file
                json_filename = os.path.join(upload_dir, 'data.json')
                with open(json_filename, 'w') as fp:
                    json.dump(json_data, fp)

                OUTPUT_COLLECTION.write('Heatmap completed successfully.\n')
                APPS_CALCULATED_SUCCESSFULLY['heatmap'] = True
            except Exception:
                OUTPUT_COLLECTION.write('Heatmap  returned an error\n#######################\n')
                OUTPUT_COLLECTION.write(traceback.format_exc())
                APPS_CALCULATED_SUCCESSFULLY['heatmap'] = False

        else:
            OUTPUT_COLLECTION.write('Contact Analysis was unsuccessful. Skipping Heatmap Analysis as it depends on it.\n')


    if CALCULATIONS_REQUESTED['densities']:
        try:
            from .big_density import save_dx
            for lg, li in SYSTEM_LIPIDS.items():
                save_dx(t, lg, li, upload_dir, task_id)

            # save protein coordinates
            new_cg = create_structure_file(coor_path, resolution)
            pdb_filename = os.path.join(upload_dir, f'{prot_name}_BB.pdb')
            new_cg.save_pdb(pdb_filename)

            OUTPUT_COLLECTION.write('dx Density completed successfully.\n')
            APPS_CALCULATED_SUCCESSFULLY['heatmap'] = True

        except Exception:
            OUTPUT_COLLECTION.write('Contact Analysis returned the following error:\n#######################\n')
            OUTPUT_COLLECTION.write(traceback.format_exc())
            APPS_CALCULATED_SUCCESSFULLY['heatmap'] = False

    ####################################################
    #######  Thickness & Curvature Analysis  ###########
    ####################################################
    PLASMA_LIPIDS = [
        # gsurf will work only for these lipids currently
        'POPX', 'DOPC', 'PIPX', 'PEPC', 'PAPC', 'DAPC', 'PUPC', 'POPE',
        'DOPE', 'PIPE', 'PQPE', 'PAPE', 'DAPE', 'PUPE', 'DUPE', 'DPSM',
        'DBSM', 'DXSM', 'POSM', 'PGSM', 'PNSM', 'BNSM', 'XNSM', 'DPG1',
        'DXG1', 'PNG1', 'XNG1', 'DPG3', 'DXG3', 'PNG3', 'XNG3', 'DPCE',
        'DXCE', 'PNCE', 'XNCE', 'PPC', 'OPC', 'IPC', 'APC', 'UPC', 'PODG',
        'PIDG', 'PADG', 'PUDG', 'CHOL', 'POPC', 'PIPC', 'POPS', 'PIPS',
        'PQPS', 'PAPS', 'DAPS', 'PUPS', 'DUPS', 'POPI', 'PIPI', 'PAPI',
        'PUPI', 'POPA', 'PIPA', 'PAPA', 'PUPA', 'POP1', 'POP2', 'POP3'
        ]
    # Regardless if the user has provided only one or a few lipids, we need to
    # check all lipids in the system. So we have to call lipid_names method here.
    if CALCULATIONS_REQUESTED['thickcurv']:
        if set(lipids.lipid_names()).issubset(PLASMA_LIPIDS):
            try:
                gsurf_dir = os.path.join(upload_dir, "gsurf_data")
                Path(gsurf_dir).mkdir(parents=True, exist_ok=True)
                cwd = os.getcwd()
                os.chdir(os.path.join(upload_dir, "gsurf_data"))

                from .gsurf import gsurf_files

                if resolution == "martini":
                    bb_name = 'BB'
                else:
                    bb_name = 'CA'

                first_bb_residues, last_bb_residues = [], []
                for i in range(first_protein.counter):
                    first = first_protein.dataframe[i][
                        (first_protein.dataframe[i].resSeq == first_protein.first_residue) &
                        (first_protein.dataframe[i].name == bb_name)
                        ].serial.to_list()[0]
                    last = first_protein.dataframe[i][
                        (first_protein.dataframe[i].resSeq == first_protein.last_residue) &
                        (first_protein.dataframe[i].name == bb_name)
                        ].serial.to_list()[0]
                    first_bb_residues.append(first)
                    last_bb_residues.append(last)

                gsurf_files(
                    gsurf_dir,
                    prot_name,
                    frames,
                    lipid_names,
                    first_protein.counter,
                    first_bb_residues,
                    last_bb_residues
                    )

                import subprocess
                from shutil import copyfile
                dest = os.path.join(gsurf_dir, "LIPIDS.lib")
                copyfile(os.path.join(os.path.join(settings.BASE_DIR, 'gsurf'), 'LIPIDS.lib'), dest)

                g_surf = subprocess.call(["g_surf -f {} -po {} -c {} -tr {} > LOG 2>&1".format(
                    os.path.join(gsurf_dir, prot_name + '.mdp'), "out.mdp", coor_path, traj_path
                )], shell=True, executable="/bin/bash")

                from .gsurf import generate_ply
                generate_ply('outie.jvx', upload_dir)
                os.chdir(upload_dir)
                os.chdir(cwd)

                OUTPUT_COLLECTION.write('Thickness & Curvature completed successfully.\n')
                APPS_CALCULATED_SUCCESSFULLY['thickcurv'] = True
            except Exception:
                OUTPUT_COLLECTION.write('Thickness & Curvature returned the following error:\n#######################\n')
                OUTPUT_COLLECTION.write(traceback.format_exc())
                APPS_CALCULATED_SUCCESSFULLY['thickcurv'] = False

    ####################################################
    ########## Save Logs & Return Metadata  ############
    ####################################################
    # saving OUTPUT_COLLECTION to log file:
    with open(os.path.join(upload_dir, 'logs.log'), 'w') as fd:
        OUTPUT_COLLECTION.seek(0)
        shutil.copyfileobj(OUTPUT_COLLECTION, fd)

    # Important: The metadata has to be JSON serializable
    rent_or_maratonomak = dict(
        prot_name=str(prot_name),
        lipid_groups=list(SYSTEM_LIPIDS.keys()),
        lipid_dict=SYSTEM_LIPIDS,
        task_id=task_id,
        radii=radii,
        groups=group_lipids,
        errors={k:str(v).lower() for k,v in APPS_CALCULATED_SUCCESSFULLY.items()},
        web_server_name="ProLint",
        web_server_version="v2.0",
    )

    if isinstance(type(user_inputs.get('email')), type(str)) and EMAIL_CONFIGURED:
        from django.core.mail import send_mail
        link = f"http://127.0.0.1:8000/results/{username}/{task_id}/"
        message = f"Your job with id: {task_id} submitted to ProLint has finished calculating.\nPlease use the following link to access it: {link}."
        send_mail('ProLint Job Submission', message, FROM_SENDER, [user_inputs.get('email')], fail_silently=False)

    return rent_or_maratonomak
