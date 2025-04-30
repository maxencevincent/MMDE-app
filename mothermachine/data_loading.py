# data_loading.py

import pandas as pd

def load_bacmman_datasets(datasets_info, separator=';'):
    """
    Load and combine one or multiple BACMMAN datasets.

    Args:
        datasets_info (dict): Dictionary of dataset specifications.
            Format:
            {
                'dataset_name1': {'filepath': 'path/to/file1.csv', 'time_addition': 10},
                'dataset_name2': {'filepath': 'path/to/file2.csv', 'time_addition': 5},
                ...
            }
        separator (str, optional): Field separator in the CSV file. Defaults to ';'.

    Returns:
        pd.DataFrame: Combined DataFrame with all datasets.
    """
    all_dfs = []

    for dataset_name, info in datasets_info.items():
        filepath = info['filepath']
        time_addition = info['time_addition']

        # Load raw data
        df = pd.read_csv(filepath, sep=separator)

        # Parse 'Indices' column (e.g., '8-6-0') into Frame, Trench, Cell
        if 'Indices' not in df.columns:
            raise ValueError(f"The file {filepath} does not contain the 'Indices' column.")

        df[['Frame_from_Indices', 'Trench', 'Cell']] = df['Indices'].str.split('-', expand=True).astype(int)

        # Convert important numeric columns
        numeric_columns = ['Size', 'MeanGFP', 'MeanRFP', 'MeanCFP', 'MeanYFP',
                           'GrowthRateArea', 'GrowthRateLength', 'Length', 'Time']

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove rows with missing Size (optional)
        if 'Size' in df.columns:
            df = df[df['Size'].notna()]

        # Add dataset metadata
        df['DatasetName'] = dataset_name
        df['TimeAddition'] = time_addition

        all_dfs.append(df)

    # Combine all datasets
    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df.reset_index(drop=True, inplace=True)

    return combined_df

