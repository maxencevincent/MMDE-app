# plotting.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np

def plot_feature_timeseries(df, datasets_frames, y_feature='Size', mode='average', time_converter=10, color_mapping=None):
    """
    Plot a selected feature over time for one or multiple datasets.

    Args:
        df (pd.DataFrame): Combined dataframe.
        datasets_frames (dict): Mapping of dataset names to their TimeAddition.
        y_feature (str): Feature to plot on Y-axis.
        mode (str): 'average' for mean ± std, 'single-cell' for individual traces.
        time_converter (int): Minutes per frame.
        color_mapping (dict): Optional color mapping for datasets.

    Returns:
        pd.DataFrame: Data used for plotting (time, feature values)
    """
    plot_data = []
    datasets = list(datasets_frames.keys())
    default_colors = color_mapping or {name: color for name, color in zip(datasets, cm.tab10.colors)}

    for dataset in datasets:
        time_addition = datasets_frames[dataset]
        subset = df[df['DatasetName'] == dataset].copy()
        subset['AdjustedTime'] = ((subset['Frame_from_Indices'] - time_addition) * time_converter) / 60

        color = default_colors.get(dataset)

        if mode == 'average':
            stats = subset.groupby('AdjustedTime')[y_feature].agg(['mean', 'std']).reset_index()
            times = stats['AdjustedTime'].values
            means = stats['mean'].values
            plt.plot(times, means, label=f'{dataset} (mean)', linewidth=2, color=color)
            plt.fill_between(times, means - stats['std'], means + stats['std'], alpha=0.3, color=color)
            stats['Dataset'] = dataset
            plot_data.append(stats.rename(columns={'mean': f'{y_feature}_mean', 'std': f'{y_feature}_std'}))

        elif mode == 'single-cell':
            for (position, trench, cell), group in subset.groupby(['PositionIdx', 'Trench', 'Cell']):
                times = group['AdjustedTime'].values
                y_values = group[y_feature].values
                plt.plot(times, y_values, alpha=0.5, color=color)
                temp_df = pd.DataFrame({'AdjustedTime': times, y_feature: y_values})
                temp_df['Dataset'] = dataset
                temp_df['Cell'] = cell
                plot_data.append(temp_df)

        else:
            raise ValueError("Mode must be either 'average' or 'single-cell'.")

    combined_plot_data = pd.concat(plot_data, ignore_index=True)
    return combined_plot_data


def plot_feature_vs_position(df, datasets_frames, y_feature='Size', color_mapping=None):
    """
    Plot a selected feature versus position (Cell) for one or multiple datasets at specified frames.

    Args:
        df (pd.DataFrame): Combined dataframe.
        datasets_frames (dict): Mapping of dataset names to frame numbers.
        y_feature (str): Feature to plot on Y-axis.
        color_mapping (dict): Optional color mapping for datasets.

    Returns:
        pd.DataFrame: Data used for plotting (position, feature values)
    """
    plot_data = []
    datasets = list(datasets_frames.keys())
    default_colors = color_mapping or {name: color for name, color in zip(datasets, cm.tab10.colors)}

    all_distances = set()
    for dataset, frame in datasets_frames.items():
        subset = df[(df['DatasetName'] == dataset) & (df['Frame_from_Indices'] == frame)].copy()
        all_distances.update(subset['Cell'].dropna().unique())
    distances = sorted(all_distances)

    width = 0.15 if len(datasets) > 1 else 0.6

    for idx, dataset in enumerate(datasets):
        frame = datasets_frames[dataset]
        subset = df[(df['DatasetName'] == dataset) & (df['Frame_from_Indices'] == frame)].copy()
        color = default_colors.get(dataset)

        for d in distances:
            values = subset[subset['Cell'] == d][y_feature].values
            if len(values) > 0:
                temp_df = pd.DataFrame({
                    'Distance': [d] * len(values),
                    y_feature: values,
                    'Dataset': dataset
                })
                plot_data.append(temp_df)
                position = d + (idx - (len(datasets)-1)/2) * width if len(datasets) > 1 else d
                plt.boxplot([values],
                            positions=[position],
                            widths=width*0.8,
                            patch_artist=True,
                            boxprops=dict(facecolor=color),
                            medianprops=dict(color='black'))

    if len(datasets) > 1:
        for dataset in datasets:
            plt.plot([], c=default_colors.get(dataset), label=dataset)

    combined_plot_data = pd.concat(plot_data, ignore_index=True)
    return combined_plot_data

# Example usage
if __name__ == "__main__":
    pass
