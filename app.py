# app.py

import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from io import BytesIO, StringIO
from matplotlib import cm
from mothermachine.data_loading import load_bacmman_datasets
from mothermachine.filtering import filter_cells
from mothermachine.plotting import plot_feature_timeseries, plot_feature_vs_position

st.title("Mother Machine Data Explorer")

# --- Dataset upload or selection ---
with st.sidebar.expander("📂 Upload or Select Datasets", expanded=True):
    uploaded_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)
    data_folder = "data/"
    available_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    selected_files = st.multiselect("Or select from local data/ folder", available_files)

datasets_info = {}

if uploaded_files:
    for file in uploaded_files:
        df_name = file.name.replace('.csv', '')
        temp_path = os.path.join(".cache", file.name)
        os.makedirs(".cache", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        datasets_info[df_name] = {"filepath": temp_path}

if selected_files:
    for file in selected_files:
        df_name = file.replace('.csv', '')
        datasets_info[df_name] = {"filepath": os.path.join(data_folder, file)}

# --- Frame & Time settings ---
if datasets_info:
    with st.sidebar.expander("🕐 Frame & Time Settings"):
        time_converter = st.number_input("Time converter: minutes per frame", min_value=1, value=10, step=1)
        for name in datasets_info:
            datasets_info[name]["frame"] = st.number_input(f"For boxplot only: Frame to analyse for {name}", min_value=0, value=5, step=1)
            datasets_info[name]["time_addition"] = st.number_input(f"For time-series only: Frame considered as 0h for {name}", min_value=0, value=0, step=1)

    loading_info = {name: {"filepath": info["filepath"], "time_addition": info["time_addition"]}
                    for name, info in datasets_info.items()}
    df = load_bacmman_datasets(loading_info)

    # --- Filtering ---
    with st.sidebar.expander("🔍 Filtering Options"):
        mother_only = st.checkbox("Mother cells only (Cell == 0)", value=False)
        remove_outliers = st.checkbox("Remove outliers")
        if remove_outliers:
            outlier_feature = st.selectbox("Outlier feature", ["Size", "Length", "MeanGFP", "MeanRFP", "MeanCFP", "MeanYFP"])
            outlier_threshold = st.number_input("Outlier threshold", min_value=0.0, value=7.0, step=0.1)

        all_positions = sorted(df['PositionIdx'].dropna().unique())
        selected_positions = st.multiselect("Select positions (optional)", all_positions, default=all_positions)

        all_trenches = sorted(df['Trench'].dropna().unique())
        selected_trenches = st.multiselect("Select trenches (optional)", all_trenches, default=all_trenches)

        df = filter_cells(df, mother_only=mother_only, selected_positions=selected_positions, selected_trenches=selected_trenches)

        if remove_outliers:
            ids_to_exclude = df.groupby(['PositionIdx', 'Trench', 'Cell'])[outlier_feature].max()
            ids_to_exclude = ids_to_exclude[ids_to_exclude > outlier_threshold].index
            for (pos, trench, cell) in ids_to_exclude:
                df = df[~((df['PositionIdx'] == pos) & (df['Trench'] == trench) & (df['Cell'] == cell))]

    st.success("Datasets loaded and filtered.")

    # --- Plot Options ---
    with st.sidebar.expander("📊 Plot Options", expanded=True):
        available_features = [col for col in df.columns if df[col].dtype in ['float64', 'int64']]
        y_feature = st.selectbox("Feature to plot", available_features)
        plot_type = st.selectbox("Plot type", ["Time-series", "Feature vs Position (boxplot)"])
        if plot_type == "Time-series":
            mode = st.selectbox("Display mode", ["average", "single-cell"])

    # --- Style settings ---
    with st.sidebar.expander("🎨 Style & Export Settings"):
        show_legend = st.checkbox("Show Legend", value=True)
        show_grid = st.checkbox("Show Grid", value=True)
        show_title = st.checkbox("Show Title", value=True)
        fig_width_mm = st.number_input("Width (mm)", 10, 300, 90)
        fig_height_mm = st.number_input("Height (mm)", 10, 300, 45)
        font_family = st.selectbox("Font", ["Arial", "Helvetica", "Times New Roman", "Courier New"])
        font_size = st.number_input("Font size", 6, 24, 8)

        palette_option = st.selectbox("Color palette", ["Default", "Set2", "viridis", "user-defined"])
        dataset_names = list(datasets_info.keys())
        color_mapping = {}
        if palette_option == "user-defined":
            for name in dataset_names:
                color_mapping[name] = st.color_picker(f"Color for {name}", value="#1f77b4")
        else:
            from matplotlib import colors
            cmap = {"Default": cm.get_cmap("tab10"),
                    "Set2": cm.get_cmap("Set2"),
                    "viridis": cm.get_cmap("viridis")}.get(palette_option, cm.get_cmap("tab10"))
            for i, name in enumerate(dataset_names):
                rgba = cmap(i % cmap.N)
                color_mapping[name] = colors.to_hex(rgba)

    # --- Axis & Label settings ---
    with st.sidebar.expander("🧭 Axes & Labels"):
        x_label = st.text_input("X-axis label", "Time (h)" if "Time" in y_feature else "Distance")
        y_label = st.text_input("Y-axis label", y_feature)
        title_label = st.text_input("Plot title", f"{y_feature} analysis")
        sci_x = st.checkbox("Scientific notation X-axis", value=False)
        sci_y = st.checkbox("Scientific notation Y-axis", value=False)
        x_min = st.number_input("X min", value=-1e6)
        x_max = st.number_input("X max", value=1e6)
        y_min = st.number_input("Y min", value=-1e6)
        y_max = st.number_input("Y max", value=1e6)

    # --- Treatment overlays ---
    shaded_areas = []
    with st.sidebar.expander("🩺 Add Treatment Areas"):
        add_area = st.checkbox("Add shaded treatment area")
        if add_area:
            use_time = st.radio("X-axis unit", ["frame", "hour"])
            num_areas = st.number_input("Number of shaded areas", min_value=1, max_value=5, value=1)
            for i in range(num_areas):
                st.markdown(f"**Area {i+1}**")
                start = st.number_input(f"Start {use_time} (area {i+1})", key=f"start_{i}")
                end = st.number_input(f"End {use_time} (area {i+1})", key=f"end_{i}")
                color = st.color_picker(f"Color (area {i+1})", value="#000000", key=f"color_{i}")
                alpha = st.slider(f"Transparency (area {i+1})", 0.0, 1.0, 0.8, step=0.05, key=f"alpha_{i}")
                shaded_areas.append({"start": start, "end": end, "color": color, "alpha": alpha, "unit": use_time})

    # --- Apply plotting style ---
    mpl.rcParams.update({
        'font.size': font_size,
        'font.family': font_family,
        'axes.labelsize': font_size,
        'axes.titlesize': font_size,
        'legend.fontsize': font_size - 2,
        'xtick.labelsize': font_size - 2,
        'ytick.labelsize': font_size - 2,
        'svg.fonttype': 'none'
    })

    # --- Main Plot Button ---
    if st.button("Generate Plot"):
        datasets_frames = {name: info["frame"] for name, info in datasets_info.items()}
        datasets_addition = {name: info["time_addition"] for name, info in datasets_info.items()}
        figsize = (fig_width_mm / 25.4, fig_height_mm / 25.4)

        plt.figure(figsize=figsize)

        if plot_type == "Time-series":
            plot_data = plot_feature_timeseries(df, datasets_addition, y_feature, mode, time_converter=time_converter, color_mapping=color_mapping)
        else:
            plot_data = plot_feature_vs_position(df, datasets_frames, y_feature, color_mapping=color_mapping)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if show_title:
            plt.title(title_label)
        if not show_legend and plt.gca().get_legend():
            plt.gca().get_legend().remove()
        if show_grid:
            plt.grid(True, axis='y')
        if sci_x:
            plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        if sci_y:
            plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        if x_min != -1e6 or x_max != 1e6:
            plt.xlim(x_min, x_max)
        if y_min != -1e6 or y_max != 1e6:
            plt.ylim(y_min, y_max)

        for area in shaded_areas:
            x1 = area['start']
            x2 = area['end']
            if area['unit'] == "frame":
                x1 = (x1 - list(datasets_addition.values())[0]) * time_converter / 60
                x2 = (x2 - list(datasets_addition.values())[0]) * time_converter / 60
            plt.axvspan(x1, x2, ymin=0, ymax=1, color=area['color'], alpha=area['alpha'])

        st.pyplot(plt.gcf())

        filename_base = f"{y_feature}_{plot_type.replace(' ', '_')}"
        buf_png = BytesIO()
        plt.savefig(buf_png, format="png")
        buf_png.seek(0)
        st.download_button("Download PNG", data=buf_png, file_name=f"{filename_base}.png", mime="image/png")

        buf_pdf = BytesIO()
        plt.savefig(buf_pdf, format="pdf")
        buf_pdf.seek(0)
        st.download_button("Download PDF", data=buf_pdf, file_name=f"{filename_base}.pdf", mime="application/pdf")

        buf_svg = StringIO()
        plt.savefig(buf_svg, format="svg")
        svg_data = buf_svg.getvalue()
        st.download_button("Download SVG", data=svg_data, file_name=f"{filename_base}.svg", mime="image/svg+xml")

        csv_buf = plot_data.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv_buf, file_name=f"{filename_base}.csv", mime="text/csv")
else:
    st.info("Please upload or select at least one CSV file to start.")

# --- Footer ---
st.markdown(
    """
    <style>
        .footer {
            position: fixed;
            bottom: 10px;
            right: 10px;
            font-size: 0.9em;
            color: grey;
        }
    </style>
    <div class="footer">
        Created by Maxence VINCENT (2025) – 📧 <a href="mailto:mvincent@imm.cnrs.fr">mvincent@imm.cnrs.fr</a>
    </div>
    """,
    unsafe_allow_html=True,
)
