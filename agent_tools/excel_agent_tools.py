import pandas as pd
import os
from typing import List, Optional, Dict, Any

def create_excel_file(
    file_path: str,
    sheet_name: str = 'Sheet1',
    data: Optional[List[List[Any]]] = None,
    headers: Optional[List[str]] = None
) -> str:
    """
    Create a new Excel file with optional data and headers.
    
    Args:
        file_path (str): Full path where the Excel file should be saved
        sheet_name (str): Name of the worksheet (default: 'Sheet1')
        data (Optional[List[List[Any]]]): 2D list of data rows and columns (can be None for empty file)
        headers (Optional[List[str]]): List of column header names
        
    Returns:
        str: Message indicating success or failure
    """
    try:
        # Ensure the directory exists
        dir_name = os.path.dirname(file_path)
        if dir_name:  # Only create if path includes a directory
            os.makedirs(dir_name, exist_ok=True)

        # Data validation
        if data is not None and headers is None:
            return f"Error: Headers must be provided if data is specified."
            
        # Ensure header count matches data column count (if data exists)
        if data and headers and len(headers) != len(data[0]):
            return f"Error: Number of headers ({len(headers)}) does not match number of data columns ({len(data[0])})."

        # Create a pandas DataFrame
        if data is not None:
            df = pd.DataFrame(data, columns=headers)
        else:
            # Create an empty DataFrame if only headers are given, or completely empty if neither
            df = pd.DataFrame(columns=headers if headers else [])

        # Write the DataFrame to an Excel file
        df.to_excel(file_path, sheet_name=sheet_name, index=False)

        abs_path = os.path.abspath(file_path)
        return f"Excel file created successfully at '{abs_path}' with sheet '{sheet_name}'."

    except Exception as e:
        return f"Error creating Excel file: {str(e)}"
