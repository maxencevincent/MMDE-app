# filtering.py
import streamlit as st

@st.cache_data

def filter_cells(df, mother_only=False, selected_positions=None, selected_trenches=None):
    """
    Filter the dataset for mother cells or all cells, and optionally by position/trench.

    Args:
        df (pd.DataFrame): Full dataset.
        mother_only (bool): If True, keep only cells where Cell == 0.
        selected_positions (list or None): If provided, keep only those PositionIdx.
        selected_trenches (list or None): If provided, keep only those Trench values.

    Returns:
        pd.DataFrame: Filtered dataframe.
    """
    if mother_only:
        df = df[df['Cell'] == 0]
    if selected_positions is not None:
        df = df[df['PositionIdx'].isin(selected_positions)]
    if selected_trenches is not None:
        df = df[df['Trench'].isin(selected_trenches)]
    return df.copy()
