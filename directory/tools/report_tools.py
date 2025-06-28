
# src/bi_dashboard_crew/tools/report_tools.py
from crewai.tools import tool
from datetime import datetime

@tool("Report Formatter Tool")
def report_formatter_tool(analysis_data: str, insights: str, trends: str) -> str:
    """Creates a formatted business report."""
    try:
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
================================================================================
                           BUSINESS INTELLIGENCE REPORT
================================================================================
Generated on: {report_date}

EXECUTIVE SUMMARY
================================================================================
Comprehensive analysis of business data with statistical summaries, 
insights, and strategic recommendations.

DATA ANALYSIS RESULTS
================================================================================
{analysis_data}

BUSINESS INSIGHTS
================================================================================
{insights}

TREND ANALYSIS
================================================================================
{trends}

STRATEGIC RECOMMENDATIONS
================================================================================
1. DATA STRATEGY
   - Implement data quality monitoring
   - Establish regular cleaning procedures
   - Consider automated validation

2. BUSINESS OPTIMIZATION
   - Focus on top-performing products
   - Develop customer retention strategies
   - Monitor KPIs regularly

3. OPERATIONAL IMPROVEMENTS
   - Streamline data collection
   - Implement real-time dashboards
   - Train staff on data-driven decisions

CONCLUSION
================================================================================
Analysis reveals important business patterns for strategic decision-making.
Regular monitoring recommended for continued optimization.

Report by: CrewAI Business Intelligence System
================================================================================
        """
        
        return report.strip()
        
    except Exception as e:
        return f"Error generating report: {str(e)}"

@tool("Executive Summary Tool")
def executive_summary_tool(full_report: str) -> str:
    """Creates executive summary from full report."""
    try:
        summary = f"""
EXECUTIVE SUMMARY - {datetime.now().strftime("%Y-%m-%d")}
==================================================

KEY FINDINGS:
- Data analysis completed successfully
- Business insights generated from statistical analysis
- Strategic recommendations provided

IMMEDIATE ACTIONS:
1. Review top-performing products
2. Implement data quality measures
3. Establish regular reporting

BUSINESS IMPACT:
- Enhanced decision-making capability
- Improved operational efficiency
- Strategic planning support

Next Steps: Implement recommendations and schedule follow-up.
        """
        
        return summary.strip()
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"