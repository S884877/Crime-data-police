import pandas as pd
import os


def process_csv(path):
    """
    Load and normalize a CSV file into a pandas DataFrame.
    
    Expected CSV columns (case-insensitive): 
    - crime_type (or 'type')
    - location (or 'place')
    - year
    - severity (optional)
    
    Args:
        path (str): Absolute path to the CSV file
        
    Returns:
        pd.DataFrame: Normalized dataframe with lowercase column names
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        pd.errors.ParserError: If CSV is malformed
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    # Read CSV file
    df = pd.read_csv(path)
    
    # Normalize column names: lowercase and replace spaces with underscores
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
    
    return df


def get_total_crimes(path):
    """
    Get the total count of crimes in the dataset.
    
    Args:
        path (str): Path to the CSV file
        
    Returns:
        dict: {'total_crimes': int, 'file': str}
    """
    df = process_csv(path)
    total = len(df)
    return {
        'total_crimes': total,
        'file': os.path.basename(path)
    }


def get_crimes_by_type(path):
    """
    Get crime counts grouped by crime type.
    
    Args:
        path (str): Path to the CSV file
        
    Returns:
        dict: {
            'group_by': 'crime_type',
            'total_crimes': int,
            'breakdown': [
                {'crime_type': 'Theft', 'count': 5},
                {'crime_type': 'Assault', 'count': 3},
                ...
            ]
        }
    """
    df = process_csv(path)
    
    # Try to find the crime_type column (handle variations)
    crime_col = None
    for col in df.columns:
        if 'crime' in col or 'type' in col:
            crime_col = col
            break
    
    if crime_col is None:
        # Fallback to common names
        crime_col = 'crime_type' if 'crime_type' in df.columns else df.columns[0]
    
    # Count crimes by type and sort in descending order
    counts = df[crime_col].fillna('Unknown').value_counts().sort_values(ascending=False)
    
    # Convert to list of dicts for JSON serialization
    breakdown = [
        {'crime_type': crime, 'count': int(count)}
        for crime, count in counts.items()
    ]
    
    return {
        'group_by': 'crime_type',
        'total_crimes': len(df),
        'breakdown': breakdown
    }


def get_crimes_by_year(path):
    """
    Get crime counts grouped by year (time series).
    
    Args:
        path (str): Path to the CSV file
        
    Returns:
        dict: {
            'group_by': 'year',
            'total_crimes': int,
            'breakdown': [
                {'year': 2020, 'count': 10},
                {'year': 2021, 'count': 15},
                ...
            ]
        }
    """
    df = process_csv(path)
    
    # Check if year column exists
    if 'year' not in df.columns:
        return {
            'error': 'year column not found in dataset',
            'available_columns': list(df.columns)
        }
    
    # Convert year to numeric and handle missing values
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df_clean = df.dropna(subset=['year'])
    
    # Count crimes by year and sort chronologically
    counts = df_clean['year'].astype(int).value_counts().sort_index()
    
    # Convert to list of dicts
    breakdown = [
        {'year': int(year), 'count': int(count)}
        for year, count in counts.items()
    ]
    
    return {
        'group_by': 'year',
        'total_crimes': len(df),
        'breakdown': breakdown
    }


def get_crimes_by_location(path):
    """
    Get crime counts grouped by location.
    
    Args:
        path (str): Path to the CSV file
        
    Returns:
        dict: {
            'group_by': 'location',
            'total_crimes': int,
            'breakdown': [
                {'location': 'Downtown', 'count': 8},
                {'location': 'Northside', 'count': 6},
                ...
            ]
        }
    """
    df = process_csv(path)
    
    # Check if location column exists
    if 'location' not in df.columns:
        return {
            'error': 'location column not found in dataset',
            'available_columns': list(df.columns)
        }
    
    # Count crimes by location
    counts = df['location'].fillna('Unknown').value_counts().sort_values(ascending=False)
    
    # Convert to list of dicts
    breakdown = [
        {'location': location, 'count': int(count)}
        for location, count in counts.items()
    ]
    
    return {
        'group_by': 'location',
        'total_crimes': len(df),
        'breakdown': breakdown
    }


# Legacy function for backward compatibility with existing frontend
def summarize_by(path, group_by='type'):
    """
    Legacy endpoint handler - routes to appropriate function.
    
    Args:
        path (str): Path to CSV file
        group_by (str): 'type', 'year', or 'location'
        
    Returns:
        list: Simplified [{label, value}, ...] format
    """
    if group_by in ('type', 'crime_type'):
        result = get_crimes_by_type(path)
        return [{'label': item['crime_type'], 'value': item['count']} 
                for item in result.get('breakdown', [])]
    elif group_by in ('year',):
        result = get_crimes_by_year(path)
        return [{'label': str(item['year']), 'value': item['count']} 
                for item in result.get('breakdown', [])]
    elif group_by in ('location', 'place'):
        result = get_crimes_by_location(path)
        return [{'label': item['location'], 'value': item['count']} 
                for item in result.get('breakdown', [])]
    else:
        return []