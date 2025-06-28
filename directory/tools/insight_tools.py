
# src/bi_dashboard_crew/tools/insight_tools.py
from crewai.tools import tool
import re

@tool("Pattern Analysis Tool")
def pattern_analysis_tool(data_summary: str) -> str:
    """Analyzes data summary to identify patterns and business insights."""
    try:
        insights = []
        
        # Sales performance analysis
        if "Total Sales" in data_summary:
            sales_match = re.search(r'Total Sales[\'"]:\s*[\'"]?\$?([\d,]+\.?\d*)', data_summary)
            if sales_match:
                total_sales = float(sales_match.group(1).replace(',', ''))
                insights.append(f"Revenue Performance: Total sales of ${total_sales:,.2f} indicates {'strong' if total_sales > 1000 else 'moderate'} business performance.")
        
        # Transaction analysis
        if "Number of Transactions" in data_summary:
            trans_match = re.search(r'Number of Transactions[\'"]:\s*(\d+)', data_summary)
            if trans_match:
                transactions = int(trans_match.group(1))
                insights.append(f"Customer Engagement: {transactions} transactions suggests {'high' if transactions > 50 else 'moderate'} customer activity.")
        
        # Product insights
        if "Top 5 Products" in data_summary:
            insights.append("Product Mix Analysis: Top 5 products show market preferences and can guide inventory decisions.")
        
        # Data quality insights
        if "Original rows" in data_summary and "After cleaning" in data_summary:
            orig_match = re.search(r'Original rows:\s*(\d+)', data_summary)
            clean_match = re.search(r'After cleaning:\s*(\d+)', data_summary)
            if orig_match and clean_match:
                orig = int(orig_match.group(1))
                clean = int(clean_match.group(1))
                if orig > clean:
                    data_loss = ((orig - clean) / orig) * 100
                    insights.append(f"Data Quality: {data_loss:.1f}% data loss during cleaning.")
        
        insights.extend([
            "Recommendations:",
            "- Monitor top-performing products for inventory optimization",
            "- Analyze seasonal trends if time-series data available",
            "- Consider customer segmentation based on patterns"
        ])
        
        return "\n".join(insights)
        
    except Exception as e:
        return f"Error generating insights: {str(e)}"

@tool("Trend Identification Tool")
def trend_identification_tool(data_summary: str) -> str:
    """Identifies trends and patterns for strategic planning."""
    try:
        trends = []
        
        # Revenue trends
        if "Average Sales" in data_summary:
            avg_match = re.search(r'Average Sales[\'"]:\s*[\'"]?\$?([\d,]+\.?\d*)', data_summary)
            if avg_match:
                avg_sales = float(avg_match.group(1).replace(',', ''))
                if avg_sales > 200:
                    trends.append("High-Value Transaction Trend: Premium customer base detected.")
                elif avg_sales < 50:
                    trends.append("Volume-Based Trend: Volume-driven business model.")
        
        trends.extend([
            "Market Analysis:",
            "- Product concentration indicates market preferences",
            "- Data completeness affects analysis accuracy",
            "- Regular monitoring recommended"
        ])
        
        return "\n".join(trends)
        
    except Exception as e:
        return f"Error identifying trends: {str(e)}"