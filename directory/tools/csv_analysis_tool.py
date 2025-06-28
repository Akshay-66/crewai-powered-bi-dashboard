
# src/bi_dashboard_crew/tools/csv_analysis_tool.py
import pandas as pd
from crewai.tools import tool

@tool("CSV Summary Analysis")
def csv_summary_tool(file_path: str) -> str:
    """
    Provides summary statistics from a CSV DataFrame: total sales, number of transactions, top products.
    
    Args:
        file_path (str): Path to the CSV file to analyze
        
    Returns:
        str: Summary statistics and insights from the CSV file
    """
    try:
        df = pd.read_csv(file_path)
        
        # Basic cleaning
        original_rows = len(df)
        df = df.dropna()
        cleaned_rows = len(df)
        
        summary = {
            'File Info': f"Original rows: {original_rows}, After cleaning: {cleaned_rows}",
            'Columns': list(df.columns)
        }
        
        # Sales analysis
        sales_cols = [col for col in df.columns if 'sales' in col.lower()]
        if sales_cols:
            total_sales = df[sales_cols[0]].sum()
            avg_sales = df[sales_cols[0]].mean()
            summary['Total Sales'] = f"${total_sales:,.2f}"
            summary['Average Sales'] = f"${avg_sales:,.2f}"
        
        summary['Number of Transactions'] = cleaned_rows
        
        # Product analysis
        product_cols = [col for col in df.columns if 'product' in col.lower()]
        if product_cols:
            top_products = df[product_cols[0]].value_counts().head(100).to_dict()
            summary['Top 100 Products'] = top_products
        
        # Numeric column analysis
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        for col in numeric_cols:
            if col.lower() not in ['sales']:
                summary[f'{col}_stats'] = {
                    'mean': round(df[col].mean(), 2),
                    'median': round(df[col].median(), 2),
                    'std': round(df[col].std(), 2)
                }
        
        return str(summary)
        
    except Exception as e:
        return f"Error processing CSV: {str(e)}"
