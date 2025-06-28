"""
CrewAI Integration Module for Streamlit BI Dashboard
This module handles the integration between Streamlit UI and CrewAI agents
"""
from directory.data_analyst import DataAnalystAgent
from directory.insight_agent import InsightAgent
from directory.report_writer import ReportWriterAgent
from crewai import Crew, Task
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import io
import base64
from typing import Dict, List, Any, Optional
import streamlit as st

class CrewAIIntegration:
    """
    Main class for integrating CrewAI with Streamlit dashboard
    """
    
    def __init__(self):
        self.crew = None
        self.agents = {}
        self.current_analysis = None
        self.progress_callback = None
    
    def initialize_crew(self):
        """Initialize CrewAI agents and crew"""
        try:
            
            # Example agent initialization (uncomment and modify based on your setup)
            
            self.agents['data_analyst'] = DataAnalystAgent()
            self.agents['insight_agent'] = InsightAgent()
            self.agents['report_writer'] = ReportWriterAgent()
            
            # Create tasks
            tasks = [
                Task(
                    description="Analyze the uploaded CSV data and provide statistical insights",
                    agent=self.agents['data_analyst']
                ),
                Task(
                    description="Generate business insights from the data analysis",
                    agent=self.agents['insight_agent']
                ),
                Task(
                    description="Create a comprehensive report with findings and recommendations",
                    agent=self.agents['report_writer']
                )
            ]
            
            # Create crew
            self.crew = Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                verbose=True
            )
            
            
            # For now, we'll use a mock setup
            # self.setup_mock_crew()
            
            return True
            
        except Exception as e:
            st.error(f"Error initializing CrewAI: {str(e)}")
            return False
    
    def setup_mock_crew(self):
        """Setup mock crew for demonstration purposes"""
        self.agents = {
            'data_analyst': MockAgent("Data Analyst"),
            'insight_agent': MockAgent("Insight Agent"),
            'report_writer': MockAgent("Report Writer")
        }
        self.crew = MockCrew(self.agents)
    
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    def update_progress(self, message: str, progress: int):
        """Update progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(message, progress)
    
    def analyze_csv_data(self, df: pd.DataFrame, analysis_options: Dict) -> Dict[str, Any]:
        """
        Main function to analyze CSV data using CrewAI
        
        Args:
            df: Pandas DataFrame with the uploaded data
            analysis_options: Dictionary with analysis preferences
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            if self.crew is None:
                if not self.initialize_crew():
                    raise Exception("Failed to initialize CrewAI")
            
            # Prepare data summary for agents
            data_summary = self.prepare_data_summary(df)
            
            # Update progress
            self.update_progress("🔍 Data Analyst Agent: Analyzing data structure...", 20)
            
            # Run data analysis
            statistical_analysis = self.run_statistical_analysis(df)
            
            self.update_progress("💡 Insight Agent: Generating business insights...", 50)
            
            # Generate business insights
            business_insights = self.generate_business_insights(df, statistical_analysis)
            
            self.update_progress("📊 Creating visualizations...", 70)
            
            # Create visualizations
            visualizations = self.create_visualizations(df, analysis_options)
            
            self.update_progress("📝 Report Writer Agent: Compiling final report...", 90)
            
            # Generate final report
            final_report = self.generate_final_report(
                df, statistical_analysis, business_insights, analysis_options
            )
            
            self.update_progress("✅ Analysis complete!", 100)
            
            # Compile results
            results = {
                'data_summary': data_summary,
                'statistical_analysis': statistical_analysis,
                'business_insights': business_insights,
                'visualizations': visualizations,
                'final_report': final_report,
                'recommendations': self.generate_recommendations(df, business_insights),
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'data_shape': df.shape,
                    'analysis_options': analysis_options
                }
            }
            
            self.current_analysis = results
            return results
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            return None
    
    def prepare_data_summary(self, df: pd.DataFrame) -> Dict:
        """Prepare data summary for agents"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'datetime_columns': datetime_cols,
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
    
    def run_statistical_analysis(self, df: pd.DataFrame) -> Dict:
        """Run statistical analysis on the data"""
        numeric_df = df.select_dtypes(include=['number'])
        
        if numeric_df.empty:
            return {
                'summary_stats': {},
                'correlations': {},
                'message': 'No numeric columns found for statistical analysis'
            }
        
        # Basic statistics
        summary_stats = numeric_df.describe().to_dict()
        
        # Correlation analysis
        correlations = numeric_df.corr().to_dict() if len(numeric_df.columns) > 1 else {}
        
        # Outlier detection using IQR method
        outliers = {}
        for col in numeric_df.columns:
            Q1 = numeric_df[col].quantile(0.25)
            Q3 = numeric_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers[col] = len(numeric_df[(numeric_df[col] < lower_bound) | (numeric_df[col] > upper_bound)])
        
        # Distribution analysis
        distributions = {}
        for col in numeric_df.columns:
            distributions[col] = {
                'skewness': float(numeric_df[col].skew()),
                'kurtosis': float(numeric_df[col].kurtosis()),
                'is_normal': abs(numeric_df[col].skew()) < 0.5  # Simple normality check
            }
        
        return {
            'summary_stats': summary_stats,
            'correlations': correlations,
            'outliers': outliers,
            'distributions': distributions,
            'numeric_columns_count': len(numeric_df.columns),
            'total_missing': numeric_df.isnull().sum().sum()
        }
    
    def generate_business_insights(self, df: pd.DataFrame, stats: Dict) -> List[str]:
        """Generate business insights from the data"""
        insights = []
        
        # Data quality insights
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        data_completeness = ((total_cells - missing_cells) / total_cells) * 100
        
        if data_completeness > 95:
            insights.append(f"Excellent data quality with {data_completeness:.1f}% completeness")
        elif data_completeness > 80:
            insights.append(f"Good data quality with {data_completeness:.1f}% completeness")
        else:
            insights.append(f"Data quality needs attention - only {data_completeness:.1f}% complete")
        
        # Size insights
        if len(df) > 10000:
            insights.append("Large dataset detected - suitable for robust statistical analysis")
        elif len(df) > 1000:
            insights.append("Medium-sized dataset - good for trend analysis")
        else:
            insights.append("Small dataset - consider collecting more data for stronger insights")
        
        # Correlation insights
        if 'correlations' in stats and stats['correlations']:
            high_corr_pairs = []
            correlations = stats['correlations']
            for col1 in correlations:
                for col2 in correlations[col1]:
                    if col1 != col2 and abs(correlations[col1][col2]) > 0.7:
                        high_corr_pairs.append((col1, col2, correlations[col1][col2]))
            
            if high_corr_pairs:
                insights.append(f"Found {len(high_corr_pairs)} strong correlations between variables")
        
        # Outlier insights
        if 'outliers' in stats:
            total_outliers = sum(stats['outliers'].values())
            if total_outliers > 0:
                insights.append(f"Detected {total_outliers} potential outliers across all numeric columns")
        
        # Distribution insights
        if 'distributions' in stats:
            normal_cols = [col for col, dist in stats['distributions'].items() if dist['is_normal']]
            if normal_cols:
                insights.append(f"{len(normal_cols)} columns show approximately normal distribution")
        
        return insights
    
    def create_visualizations(self, df: pd.DataFrame, options: Dict) -> Dict:
        """Create visualizations based on the data and options"""
        visualizations = {}
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        chart_types = options.get('chart_types', ['Line Charts', 'Bar Charts'])
        
        # Correlation heatmap
        if len(numeric_cols) > 1 and 'Heatmaps' in chart_types:
            corr_matrix = df[numeric_cols].corr()
            visualizations['correlation_heatmap'] = px.imshow(
                corr_matrix,
                title="Correlation Matrix",
                color_continuous_scale="RdBu_r",
                aspect="auto"
            )
        
        # Distribution plots
        if len(numeric_cols) > 0 and 'Distribution' in chart_types:
            for col in numeric_cols[:3]:  # Limit to first 3 columns
                visualizations[f'distribution_{col}'] = px.histogram(
                    df, x=col,
                    title=f"Distribution of {col}",
                    nbins=30,
                    marginal="box"
                )
        
        # Bar charts for categorical data
        if len(categorical_cols) > 0 and 'Bar Charts' in chart_types:
            for col in categorical_cols[:2]:  # Limit to first 2 columns
                value_counts = df[col].value_counts().head(10)
                visualizations[f'bar_{col}'] = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Top Values in {col}"
                )
        
        # Scatter plots
        if len(numeric_cols) >= 2 and 'Scatter Plots' in chart_types:
            visualizations['scatter_plot'] = px.scatter(
                df, x=numeric_cols[0], y=numeric_cols[1],
                title=f"{numeric_cols[0]} vs {numeric_cols[1]}"
            )
        
        # Line charts (if there's a time component or sequential data)
        if len(numeric_cols) > 0 and 'Line Charts' in chart_types:
            # Create a simple line chart with index
            visualizations['trend_line'] = px.line(
                df.head(100),  # Limit to 100 points for performance
                y=numeric_cols[0],
                title=f"Trend Analysis: {numeric_cols[0]}"
            )
        
        return visualizations
    
    def generate_final_report(self, df: pd.DataFrame, stats: Dict, 
                            insights: List[str], options: Dict) -> str:
        """Generate comprehensive final report"""
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# Business Intelligence Analysis Report

**Generated on:** {report_date}
**Analysis Depth:** {options.get('analysis_depth', 'Basic')}

## Executive Summary

This report presents a comprehensive analysis of your business data containing {len(df):,} records across {len(df.columns)} columns. Our AI agents have identified key patterns, trends, and actionable insights to support your decision-making process.

## Dataset Overview

- **Total Records:** {len(df):,}
- **Total Columns:** {len(df.columns)}
- **Numeric Columns:** {len(df.select_dtypes(include=['number']).columns)}
- **Categorical Columns:** {len(df.select_dtypes(include=['object']).columns)}
- **Data Completeness:** {((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}%

## Key Findings

"""
        
        # Add insights
        for i, insight in enumerate(insights, 1):
            report += f"{i}. {insight}\n\n"
        
        # Add statistical summary
        if 'summary_stats' in stats and stats['summary_stats']:
            report += "\n## Statistical Summary\n\n"
            report += "Key metrics for numeric columns:\n\n"
            
            for col, col_stats in stats['summary_stats'].items():
                if isinstance(col_stats, dict):
                    mean_val = col_stats.get('mean', 0)
                    std_val = col_stats.get('std', 0)
                    min_val = col_stats.get('min', 0)
                    max_val = col_stats.get('max', 0)
                    
                    report += f"**{col}:**\n"
                    report += f"- Mean: {mean_val:.2f}\n"
                    report += f"- Standard Deviation: {std_val:.2f}\n"
                    report += f"- Range: {min_val:.2f} to {max_val:.2f}\n\n"
        
        # Add correlation insights
        if 'correlations' in stats and stats['correlations']:
            report += "\n## Correlation Analysis\n\n"
            report += "Strong correlations detected between variables may indicate:\n"
            report += "- Related business processes\n"
            report += "- Potential redundancy in data collection\n"
            report += "- Opportunities for predictive modeling\n\n"
        
        # Add recommendations section
        report += "\n## Strategic Recommendations\n\n"
        report += "Based on our analysis, we recommend:\n\n"
        report += "1. **Data Quality Enhancement:** "
        if df.isnull().sum().sum() > 0:
            report += "Address missing data to improve analysis accuracy\n"
        else:
            report += "Maintain current high data quality standards\n"
        
        report += "2. **Process Optimization:** Focus on variables showing strong correlations\n"
        report += "3. **Monitoring Setup:** Implement regular tracking of key metrics\n"
        report += "4. **Further Analysis:** Consider advanced analytics for deeper insights\n\n"
        
        report += "\n## Methodology\n\n"
        report += "This analysis was conducted using AI agents specialized in:\n"
        report += "- **Data Analysis:** Statistical examination and pattern detection\n"
        report += "- **Business Intelligence:** Insight generation and trend identification\n"
        report += "- **Report Generation:** Comprehensive documentation and recommendations\n\n"
        
        report += "---\n*Report generated by AI-Powered BI Dashboard*"
        
        return report
    
    def generate_recommendations(self, df: pd.DataFrame, insights: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Data quality recommendations
        missing_data = df.isnull().sum().sum()
        if missing_data > 0:
            recommendations.append(f"Address {missing_data} missing values to improve data completeness")
        
        # Size-based recommendations
        if len(df) < 1000:
            recommendations.append("Consider collecting more data for more robust statistical analysis")
        
        # Column-based recommendations
        numeric_cols = len(df.select_dtypes(include=['number']).columns)
        if numeric_cols == 0:
            recommendations.append("Add numeric metrics to enable quantitative analysis")
        elif numeric_cols < 3:
            recommendations.append("Consider adding more quantitative measures for deeper insights")
        
        # General recommendations
        recommendations.extend([
            "Implement regular data quality monitoring",
            "Set up automated reporting for key metrics",
            "Consider advanced analytics for predictive insights",
            "Establish data governance processes"
        ])
        
        return recommendations[:5]  # Limit to top 5 recommendations

class MockAgent:
    """Mock agent for demonstration purposes"""
    def __init__(self, name: str):
        self.name = name
    
    def analyze(self, data):
        return f"Analysis complete by {self.name}"

class MockCrew:
    """Mock crew for demonstration purposes"""
    def __init__(self, agents: Dict):
        self.agents = agents
    
    def kickoff(self, inputs):
        return {"status": "success", "results": "Mock analysis complete"}

# Utility functions for Streamlit integration

def create_progress_tracker():
    """Create progress tracking components for Streamlit"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(message: str, progress: int):
        status_text.text(message)
        progress_bar.progress(progress)
    
    return update_progress

def run_crew_analysis(df: pd.DataFrame, analysis_options: Dict) -> Optional[Dict]:
    """
    Main function to run CrewAI analysis with Streamlit integration
    
    Args:
        df: Pandas DataFrame with uploaded data
        analysis_options: Dictionary with analysis preferences
        
    Returns:
        Analysis results or None if failed
    """
    try:
        # Initialize CrewAI integration
        crew_integration = CrewAIIntegration()
        
        # Set up progress tracking
        progress_callback = create_progress_tracker()
        crew_integration.set_progress_callback(progress_callback)
        
        # Run analysis
        results = crew_integration.analyze_csv_data(df, analysis_options)
        
        if results:
            st.success("✅ Analysis completed successfully!")
            return results
        else:
            st.error("❌ Analysis failed. Please try again.")
            return None
            
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return None

def format_results_for_display(results: Dict) -> Dict:
    """Format analysis results for Streamlit display"""
    if not results:
        return {}
    
    formatted = {
        'insights': results.get('business_insights', []),
        'visualizations': results.get('visualizations', {}),
        'summary_stats': pd.DataFrame(results.get('statistical_analysis', {}).get('summary_stats', {})),
        'report': results.get('final_report', ''),
        'recommendations': results.get('recommendations', []),
        'metadata': results.get('metadata', {})
    }
    
    return formatted