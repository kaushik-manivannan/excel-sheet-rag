import pandas as pd

def get_sheet_names(excel_file_path):
    """Get all sheet names from an Excel file."""
    excel_data = pd.read_excel(excel_file_path, sheet_name=None)
    return list(excel_data.keys())

def get_column_types(excel_file_path, sheet_name):
    """
    Get column types for a specific sheet.
    Returns a dictionary mapping column names to data types.
    """
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    return {col: str(dtype) for col, dtype in df.dtypes.items()}

def detect_date_columns(excel_file_path, sheet_name):
    """
    Detect columns that contain date values.
    Returns a list of column names that likely contain dates.
    """
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    date_columns = []
    
    for col in df.columns:
        # Check if pandas detected it as datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_columns.append(col)
        else:
            # Try to convert to datetime to see if it's possible
            try:
                pd.to_datetime(df[col], errors='raise')
                date_columns.append(col)
            except:
                pass
    
    return date_columns

def get_column_statistics(excel_file_path, sheet_name, column):
    """
    Get basic statistics for a numeric column.
    """
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    
    if column not in df.columns:
        return None
    
    # Check if the column is numeric
    if pd.api.types.is_numeric_dtype(df[column]):
        return {
            "min": df[column].min(),
            "max": df[column].max(),
            "mean": df[column].mean(),
            "median": df[column].median(),
            "std": df[column].std(),
            "unique_values": df[column].nunique()
        }
    else:
        # For non-numeric columns, just return count stats
        return {
            "unique_values": df[column].nunique(),
            "most_common": df[column].value_counts().index[0] if not df[column].empty else None,
            "null_count": df[column].isnull().sum()
        }