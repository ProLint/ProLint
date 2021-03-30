import os
import pandas as pd
import colorcet as cc
from django.conf import settings

from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.layouts import row
from bokeh.transform import linear_cmap

def scatter_handler(doc: Document) -> None:
    """
    Handler function for the scatter application.
    """

    # Load data
    task_id = doc.session_context.request.arguments.get('task_id')
    username = doc.session_context.request.arguments.get('username')
    user_dir = os.path.join(settings.USER_DATA, username)
    path_to_db = os.path.join(user_dir, task_id)
    conn = os.path.join(path_to_db, task_id + '.csv')
    df = pd.read_csv(conn)

    # widgets
    radii = [str(x) for x in df.Radius.unique()]
    number = Slider(title="Value Cutoff", value=0, start=0, end=4, step=0.1, width=150)
    residue = TextInput(title="Residue name (3 letter code):", width=200)
    gpcr = Select(title="Proteins", value=list(df.Protein.unique())[0],
                options=list(df.Protein.unique()), width=100)
    lipid = Select(title="Lipids", value=list(df.Lipids.unique())[0],
                options=list(df.Lipids.unique()), width=100)
    radius = Select(title="Radius", value=radii[-1], options=radii, width=100)
    options = list(df.columns)[:-5] + ['ResID']
    x_axis = Select(title="X Axis", options=options, value="ResID", width=150)
    y_axis = Select(title="Y Axis", options=options, value=options[0], width=150)

    # colors and plotting
    cc_colors = [x for x in cc.all_original_names() if x.startswith('linear') or x.startswith('rainbow')]
    cmap = Select(title="Colormap", options=cc_colors, value='linear_kryw_0_100_c71', width=150)
    # Create Column Data Source that will be used by the plot
    source = ColumnDataSource(data=dict(x=[], y=[], ResName=[], ResID=[], Protein=[]))
    TOOLTIPS=[
        ("ResName", "@ResName"),
        ("ResID", "@ResID"),
        ("Value", "@y")
    ]
    point_color_mapper = linear_cmap(field_name='y', palette=cc.CET_L19,
                        low=df[df.Protein == gpcr.value][y_axis.value].min(),
                        high=df[df.Protein == gpcr.value][y_axis.value].max())
    p = figure(plot_height=400, plot_width=800, tooltips=TOOLTIPS,)

    circle_plot = p.circle(x="x", y="y", source=source, line_color='black', fill_color=point_color_mapper, size=7)
    circle_object = {'circle': circle_plot}

    # make plot pretty
    p.toolbar.autohide = True
    p.axis.axis_label_text_font_size = "12pt"
    p.axis.axis_label_text_font_style = "bold"
    p.title.align = 'center'

    def update(df):
        y_value = y_axis.value
        x_value = x_axis.value

        df = df[
            (df[y_value] >= number.value) &
            (df['Protein'] == gpcr.value) &
            (df['Lipids'] == lipid.value) &
            (df['Radius'] == float(radius.value))
        ]
        if (residue.value != ""):
            df = df[df.ResName.str.contains(residue.value.upper())==True]

        point_color_mapper = linear_cmap(field_name='y', palette=cc.palette[cmap.value],
                            low=df[df.Protein == gpcr.value][y_value].min(),
                            high=df[df.Protein == gpcr.value][y_value].max())

        circle_object['circle'].glyph.fill_color = point_color_mapper

        p.xaxis.axis_label = x_value
        p.yaxis.axis_label = y_value
        p.title.text = "Showing %d Data Points  " % len(df)

        source.data = dict(
            x=df[x_value],
            y=df[y_value],
            ResName=df["ResName"],
            ResID=df["ResID"],
            Protein=df["Protein"],
        )

    # add controls
    controls = [number, gpcr, lipid, radius, y_axis, x_axis, residue, cmap]
    for control in controls:
        control.on_change('value', lambda attr, old, new: update(df))

    # build layout
    # TODO: this should be made easier to read
    sizing_mode = 'scale_width'
    inputs2 = row([gpcr, lipid, radius, residue], sizing_mode=sizing_mode)
    inputs3 = row([number, x_axis, y_axis, cmap], sizing_mode=sizing_mode)
    layout1 = layout([[inputs2]], sizing_mode=sizing_mode)
    layout2 = layout([p], sizing_mode=sizing_mode)
    layout3 = layout([inputs3], sizing_mode="scale_width")

    # render
    update(df)
    doc.add_root(layout1)
    doc.add_root(layout2)
    doc.add_root(layout3)
    doc.title = "Point Application"
