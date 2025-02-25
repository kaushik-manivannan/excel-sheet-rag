import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import json

class VisualizationTool:
    """Tool for generating visualizations from Excel data."""
    
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
    
    def generate_chart(self, params_str):
        """
        Generate a chart based on Excel data.
        
        Args:
            params_str: JSON string with chart parameters
            
        Returns:
            String containing base64-encoded image
        """
        try:
            # Parse parameters
            params = json.loads(params_str) if isinstance(params_str, str) else params_str
            
            sheet_name = params.get("sheet_name")
            x_column = params.get("x_column")
            y_column = params.get("y_column")
            chart_type = params.get("chart_type", "line").lower()
            
            if not sheet_name or not x_column or not y_column:
                return "Missing required parameters: sheet_name, x_column, and y_column"
            
            # Load Excel data
            df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
            
            # Verify columns exist
            if x_column not in df.columns:
                return f"Column '{x_column}' not found in sheet '{sheet_name}'"
            if y_column not in df.columns:
                return f"Column '{y_column}' not found in sheet '{sheet_name}'"
            
            # Apply filters if specified
            filter_column = params.get("filter_column")
            filter_value = params.get("filter_value")
            
            if filter_column and filter_value is not None:
                if filter_column not in df.columns:
                    return f"Filter column '{filter_column}' not found in sheet '{sheet_name}'"
                
                df = df[df[filter_column] == filter_value]
            
            # Set up the figure
            plt.figure(figsize=(10, 6))
            
            # Generate the appropriate chart
            if chart_type == "line":
                plt.plot(df[x_column], df[y_column], marker='o')
            elif chart_type == "bar":
                plt.bar(df[x_column], df[y_column])
            elif chart_type == "scatter":
                plt.scatter(df[x_column], df[y_column])
            elif chart_type == "pie":
                # For pie charts, we need to handle differently
                plt.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')
            else:
                return f"Unsupported chart type: {chart_type}"
            
            # Set labels and title
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.title(f"{chart_type.capitalize()} Chart: {y_column} vs {x_column}")
            
            # Rotate x-axis labels if needed
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert plot to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            
            # Return with a message
            return f"Here's the {chart_type} chart showing {y_column} vs {x_column}:\n\ndata:image/png;base64,{image_base64}"
            
        except Exception as e:
            return f"Error generating chart: {str(e)}"