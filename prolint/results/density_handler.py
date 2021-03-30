import os
import numpy as np
import pandas as pd
import colorcet as cc
import sqlite3 as sql
import matplotlib as mpl
import matplotlib.cm as cm
from django.conf import settings
from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.layouts import layout, column, row
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, BasicTickFormatter
from bokeh.models.widgets import Slider, Select, RangeSlider

def density_handler(doc: Document) -> None:
    """
    Handler function for the density application.
    """

    task_id = doc.session_context.request.arguments.get('task_id')
    username = doc.session_context.request.arguments.get('username')
    user_dir = os.path.join(settings.USER_DATA, username)
    path_to_db = os.path.join(user_dir, task_id)

    try:
        conn = os.path.join(path_to_db, task_id + '.csv')
        df = pd.read_csv(conn)

        proteins = list(df.Protein.unique())
        lipids = list(df.Lipids.unique())
    except:
        proteins, lipids = [], []

        for o in os.listdir(path_to_db):
            key = o.split('/')[-1]
            if key.endswith('.npy'):
                if key.startswith('prot_'):
                    proteins.append('Protein(s)')
                else:
                    lipid = key.split('_')[0]
                    lipids.append(lipid)

    all_mpl_cmaps = [
                'viridis', 'plasma', 'inferno', 'cividis',
                'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                'RdYlBu', 'RdYlGn', 'Spectral','Spectral_r', 'coolwarm', 'coolwarm_r', 'seismic',
                'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
                'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
    ]

    #TODO: globals declaration should not be necessary anymore.
    global prot_xyz
    prot_xyz = np.load(os.path.join(path_to_db, "prot_" + task_id + '.npy'))

    global l_xyz
    global x_min, x_max, y_min, y_max, z_min, z_max

    l_xyz = np.load(os.path.join(path_to_db, lipids[0] + "_" + task_id + '.npy'))


    x_min, x_max = l_xyz[:, 0].min(), l_xyz[:, 0].max()
    y_min, y_max = l_xyz[:, 1].min(), l_xyz[:, 1].max()
    z_min, z_max = l_xyz[:, 2].min(), l_xyz[:, 2].max()

    # widgets
    color_map = Select(title="Colormap", value="viridis",
                    options=all_mpl_cmaps, width=120)

    lipid = Select(title="Lipids", value=lipids[0],
                options=lipids, width=100)

    denstype = Select(title="Density Type", value="All Proteins",
                    options=["All Proteins", "Average"], width=120)

    number = Slider(title="Number of Bins", value=380, start=80, end=500, step=10, width=200)

    protein = Select(title="Show Protein", value="No",
                    options=["Yes", "No"], width=90)

    gpcr = Select(title="Protein", value=proteins[0],
                options=proteins, width=130)

    zrange = RangeSlider(start=z_min, end=z_max,
                        value=(z_min, z_max), step=0.2, title="Z-Axis Range",
                        callback_policy='mouseup', width=352)

    cbar_range = Slider(value=256, start=0, end=256, step=1, height=600,
                        orientation='vertical', callback_policy='mouseup', margin=(15, 0),
                        tooltips=False, show_value=False)

    # colorschemes
    colormap =cm.get_cmap(color_map.value)
    bokehpalette = [mpl.colors.rgb2hex(m) for m in colormap(np.arange(colormap.N))]

    def lipid_density(array, bins=160):
        """Given a 2D array, containing the x, y values of a lipid,
        return its histogram with edges."""
        x = array[:, 0]
        y = array[:, 1]

        lipid, e1, e2 = np.histogram2d(x, y, density=True, bins=bins)

        return lipid, e1, e2


    # Plot histogram image
    H, xe, ye = lipid_density(l_xyz, number.value)
    minx = np.abs(xe.min())
    miny = np.abs(ye.min())

    p1 = figure(plot_height=640, plot_width=640,  tools='')
    image_source = ColumnDataSource(data=dict(image=[]))
    img = p1.image(image="image", x=xe[0], y=ye[0], dw=xe[-1] + minx, dh=ye[-1] + miny, palette=bokehpalette, source=image_source)

    circle_prot_source = ColumnDataSource(data=dict(x1=prot_xyz[:, 0], y1=prot_xyz[:, 1]))
    p1.circle(x="x1", y="y1", source=circle_prot_source, size=2, fill_alpha=0.2)

    cb_palette = LinearColorMapper(palette=bokehpalette, low=H.min(), high=H.max())
    color_bar = ColorBar(color_mapper=cb_palette, width=8,  location=(0,0), label_standoff=10)
    color_bar.formatter = BasicTickFormatter(use_scientific=False)
    p1.add_layout(color_bar, 'right')

    # Make graph pretty
    p1.xgrid.grid_line_color = None
    p1.ygrid.grid_line_color = None
    p1.xaxis.major_tick_line_color = None
    p1.xaxis.minor_tick_line_color = None
    p1.yaxis.major_tick_line_color = None
    p1.yaxis.minor_tick_line_color = None
    p1.xaxis.major_label_text_font_size = '0pt'
    p1.yaxis.major_label_text_font_size = '0pt'
    p1.grid.visible = False
    p1.toolbar.logo = None
    p1.toolbar_location = None


    def update_all(cond=False, cmap=False):
        """
        Update the image showing all proteins.
        """
        if cond:
            # For efficiency execute only if GPCR structure changes
            global l_xyz
            global x_min, x_max, y_min, y_max, z_min, z_max

            l_xyz = np.load(os.path.join(path_to_db, str(lipid.value) + "_" + task_id + '.npy'))
            x_min, x_max = l_xyz[:, 0].min(), l_xyz[:, 0].max()
            y_min, y_max = l_xyz[:, 1].min(), l_xyz[:, 1].max()
            z_min, z_max = l_xyz[:, 2].min(), l_xyz[:, 2].max()
            zrange.start = z_min
            zrange.end   = z_max

            index = np.where((l_xyz[:, 2] > zrange.value[0]) &
                            (l_xyz[:, 2] < zrange.value[1]))
            l_xyz_new = l_xyz[index]
        else:
            l_xyz_new = l_xyz

        if cmap:
            # For efficiency execute only if image colormap changes
            cb_cut_value = 256 - cbar_range.value

            cmap = color_map.value
            colormap = cm.get_cmap(cmap)
            bokehpalette = [mpl.colors.rgb2hex(m) for m in colormap(np.arange(colormap.N))]
            bp_i = 0
            while bp_i < len(bokehpalette[:cb_cut_value]):
                bokehpalette[bp_i] = '#ffffff'
                bp_i += 1

            img.glyph.color_mapper.palette = bokehpalette
            color_bar.color_mapper.palette = bokehpalette

        # Update histogram image
        H, xe, ye = lipid_density(l_xyz_new, number.value)
        minx = np.abs(xe.min())
        miny = np.abs(ye.min())

        img.glyph.dw = xe[-1] + minx
        img.glyph.dh = ye[-1] + miny

        # update image source
        image_source.data = dict(image=[H])

    def update_protein(cond=False):
        """
        Update the protein representation.
        """
        if cond:
            # For efficiency execute only if GPCR structure changes
            global prot_xyz

        if protein.value == "Yes":
            circle_prot_source.data = dict(
                x1=prot_xyz[:, 0],
                y1=prot_xyz[:, 1]
            )

        elif protein.value == "No":
            circle_prot_source.data = dict(
                x1=[],
                y1=[]
            )

    def update_cbar():

        cb_cut_value = 256-cbar_range.value

        cmap = color_map.value
        colormap = cm.get_cmap(cmap)
        bokehpalette = [mpl.colors.rgb2hex(m) for m in colormap(np.arange(colormap.N))]

        bp_i = 0
        while bp_i < len(bokehpalette[:cb_cut_value]):
            bokehpalette[bp_i] = '#ffffff'
            bp_i += 1

        img.glyph.color_mapper.palette = bokehpalette
        color_bar.color_mapper.palette = bokehpalette


    # event listeners
    controls = [lipid, zrange, gpcr]
    for control in controls:
        control.on_change('value', lambda attr, old, new: update_denstype(cond=True))

    number.on_change('value', lambda attr, old, new: update_denstype())
    color_map.on_change('value', lambda attr, old, new: update_denstype(cmap=True))
    protein.on_change('value', lambda attr, old, new: update_protein())
    denstype.on_change('value', lambda attr, old, new: update_denstype())
    cbar_range.on_change('value', lambda attr, old, new: update_cbar())

    # deal with what gets updated and what not.
    def update_denstype(cond=False, cmap=False):
        update_all(cond, cmap)
        update_protein(cond)

    update_denstype()
    input1 = row([gpcr, lipid, color_map, protein])
    input2 = row([p1, cbar_range])
    input3 = row([number, zrange])
    input3 = column([input1, input2, input3])

    l = layout([input3])

    doc.add_root(l)
    doc.title = "Density App"
