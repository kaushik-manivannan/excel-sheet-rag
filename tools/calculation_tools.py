from langchain.tools import StructuredTool
import pandas as pd
import json

class CalculationTool:
    """Tool for performing calculations on Excel data."""
    
    def __init__(self, excel_file_path, sheets_info):
        self.excel_file_path = excel_file_path
        self.sheets_info = sheets_info
    
    def run_calculation(self, calculation_type: str, sheet_name: str, column: str, filter_column: str = None, filter_value: str = None, other_column: str = None):
        """
        Run calculations on Excel data based on parameters.
        
        Args:
            calculation_type: Type of calculation (sum, average, min, max, etc.)
            sheet_name: Name of the Excel sheet
            column: Column to perform calculation on
            filter_column: Optional column to filter by
            filter_value: Optional value to filter for
            other_column: Optional second column for correlation calculations
            
        Returns:
            String containing calculation results
        """
        try:
            # Check if sheet exists
            if sheet_name not in self.sheets_info:
                available_sheets = list(self.sheets_info.keys())
                return f"Worksheet named '{sheet_name}' not found. Available sheets are: {', '.join(available_sheets)}"
            
            # Load Excel data
            df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
            
            # Verify column exists
            if column not in df.columns:
                available_columns = list(df.columns)
                return f"Column '{column}' not found in sheet '{sheet_name}'. Available columns are: {', '.join(available_columns)}"
            
            # Apply filters if specified
            if filter_column and filter_value is not None:
                if filter_column not in df.columns:
                    return f"Filter column '{filter_column}' not found in sheet '{sheet_name}'"
                
                df = df[df[filter_column] == filter_value]
            
            # Perform calculation
            calculation_type = calculation_type.lower()
            
            if calculation_type == "sum":
                result = df[column].sum()
                return f"Sum of '{column}' in '{sheet_name}': {result}"
                
            elif calculation_type == "average":
                result = df[column].mean()
                return f"Average of '{column}' in '{sheet_name}': {result}"
                
            elif calculation_type == "min":
                result = df[column].min()
                return f"Minimum value of '{column}' in '{sheet_name}': {result}"
                
            elif calculation_type == "max":
                result = df[column].max()
                return f"Maximum value of '{column}' in '{sheet_name}': {result}"
                
            elif calculation_type == "count":
                result = len(df)
                return f"Count of rows for '{column}' in '{sheet_name}': {result}"
                
            elif calculation_type == "unique":
                result = df[column].nunique()
                return f"Number of unique values in '{column}' in '{sheet_name}': {result}"
                
            elif calculation_type == "correlation":
                if not other_column:
                    return "Missing required parameter: other_column for correlation"
                
                if other_column not in df.columns:
                    return f"Column '{other_column}' not found in sheet '{sheet_name}'"
                
                result = df[column].corr(df[other_column])
                return f"Correlation between '{column}' and '{other_column}' in '{sheet_name}': {result}"
                
            else:
                return f"Unsupported calculation type: {calculation_type}"
                
        except Exception as e:
            return f"Error performing calculation: {str(e)}"
    
    def get_tool(self):
        """Return a StructuredTool that wraps this function"""
        # Create a description that includes available sheets and their columns
        sheets_description = "Available sheets: "
        for sheet_name, info in self.sheets_info.items():
            sheets_description += f"\n- {sheet_name}: {', '.join(info['columns'])}"
        
        return StructuredTool.from_function(
            func=self.run_calculation,
            name="CalculateValue",
            description=f"Calculate values from Excel data. Provide calculation_type (e.g., sum, average, min, max, count), sheet_name, and column name. {sheets_description}",
        )