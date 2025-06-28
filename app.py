import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO, BytesIO
import base64
import json
import time
from datetime import datetime
import os

# Import CrewAI integration
from application.crew_integration import run_crew_analysis, format_results_for_display

# For PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Configure page
st.set_page_config(
    page_title="CrewAI-Powered BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with dark mode support
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
            
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    /* Upload section with dark mode support */
    .upload-section {
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #ddd;
        text-align: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    /* Light mode upload section */
    [data-theme="light"] .upload-section {
        background: #f8f9fa;
        border-color: #ddd;
        color: #333;
    }
    
    /* Dark mode upload section */
    [data-theme="dark"] .upload-section {
        background: #262730;
        border-color: #4a4a4a;
        color: #fafafa;
    }
    
    /* Auto-detect system theme */
    @media (prefers-color-scheme: dark) {
        .upload-section {
            background: #262730;
            border-color: #4a4a4a;
            color: #fafafa;
        }
    }
    
    @media (prefers-color-scheme: light) {
        .upload-section {
            background: #f8f9fa;
            border-color: #ddd;
            color: #333;
        }
    }
    
    .insights-section {
        background: #fff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .progress-container {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Dark mode adjustments */
    [data-theme="dark"] .insights-section {
        background: #262730;
        color: #fafafa;
    }
    
    [data-theme="dark"] .progress-container {
        background: #262730;
        color: #fafafa;
    }
    
    [data-theme="dark"] .metric-card {
        background: #262730;
        color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'crew_output' not in st.session_state:
        st.session_state.crew_output = None
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = None

def create_sidebar():
    """Create sidebar with instructions and options"""
    with st.sidebar:
        st.markdown("### 🔧 Dashboard Controls")
        
        st.markdown("""
        #### 📋 Instructions:
        1. **Enter API Key**: Add your Gemini API key for AI analysis
        2. **Upload CSV**: Select your business data file
        3. **AI Analysis**: Our agents will analyze your data
        4. **View Results**: Explore insights and visualizations
        5. **Download Report**: Get your complete analysis
        """)
        
        st.markdown("---")
        
        # API Key Section
        st.markdown("### 🔑 AI Configuration")
        
        # API Key help link
        st.markdown("""
        **Get your Gemini API Key:**
        
        📡 [Get API Key from Google AI Studio](https://aistudio.google.com/u/3/apikey)
        
        *Free tier available with generous limits*
        """)
        
        # API Key input
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="Enter your Gemini API key here...",
            help="Your API key is stored securely for this session only"
        )
        
        # API Key status
        if api_key:
            if len(api_key) > 20:  # Basic validation
                st.success("✅ API Key configured")
                # Store in session state
                st.session_state['gemini_api_key'] = api_key
            else:
                st.error("❌ Invalid API Key format")
        else:
            st.info("ℹ️ API Key required for AI analysis")
        
        st.markdown("---")
        
        # Analysis Options
        st.markdown("### ⚙️ Analysis Options")
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Basic", "Detailed", "Comprehensive"],
            help="Choose the depth of analysis"
        )
        
        chart_types = st.multiselect(
            "Chart Types",
            ["Line Charts", "Bar Charts", "Scatter Plots", "Heatmaps", "Distribution"],
            default=["Line Charts", "Bar Charts"],
            help="Select visualization types"
        )
        
        st.markdown("---")
        
        # File Upload Section
        st.markdown("### 📁 File Upload")
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Upload your business data in CSV format"
        )
        
        return uploaded_file, analysis_depth, chart_types, api_key

def display_header():
    """Display main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 CrewAI-Powered Business Intelligence Dashboard</h1>
        <p>Upload your data and let our AI agents provide deep insights and automated reporting</p>
    </div>
    """, unsafe_allow_html=True)


def display_upload_section():
    """Display upload section when no file is uploaded"""
    st.markdown("""
    <div class="upload-section">
        <h3>📊 Ready to Analyze Your Data?</h3>
        <p>Upload your CSV file using the sidebar to get started with AI-powered analysis</p>
        <p><strong>Supported formats:</strong> CSV files with headers</p>
        <p><strong>What you'll get:</strong> Automated insights, visualizations, and comprehensive reports</p>
    </div>
    """, unsafe_allow_html=True)

def validate_csv_data(df):
    """Validate uploaded CSV data"""
    issues = []
    
    if df.empty:
        issues.append("CSV file is empty")
    
    if len(df.columns) < 2:
        issues.append("CSV should have at least 2 columns")
    
    # Check for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) == 0:
        issues.append("No numeric columns found for analysis")
    
    return issues

def display_data_preview(df):
    """Display data preview and basic statistics"""
    st.markdown("### 📋 Data Preview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        numeric_cols = len(df.select_dtypes(include=['number']).columns)
        st.metric("Numeric Columns", numeric_cols)
    with col4:
        missing_data = df.isnull().sum().sum()
        st.metric("Missing Values", missing_data)
    
    # Data preview
    st.markdown("#### Sample Data:")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Column information
    st.markdown("#### Column Information:")
    col_info = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes,
        'Non-Null Count': df.count(),
        'Missing %': ((df.isnull().sum() / len(df)) * 100).round(2)
    })
    st.dataframe(col_info, use_container_width=True)

def run_crew_analysis_with_ui(df, analysis_depth="Basic", chart_types=None, api_key=None):
    """Run CrewAI analysis with proper UI integration"""
    if chart_types is None:
        chart_types = ["Line Charts", "Bar Charts"]
    
    # Check if API key is provided
    if not api_key:
        st.error("🔑 Gemini API Key is required for AI analysis!")
        st.info("Please enter your API key in the sidebar to proceed.")
        return None
    
    analysis_options = {
        'analysis_depth': analysis_depth,
        'chart_types': chart_types,
        'api_key': api_key
    }
    
    # Create progress container
    progress_container = st.container()
    
    with progress_container:
        st.markdown("### 🔄 AI Analysis in Progress")
        
        # Show progress steps
        progress_steps = [
            "🔑 Validating API credentials...",
            "📊 Analyzing data structure...",
            "🤖 Running AI analysis...",
            "📈 Generating insights...",
            "📋 Preparing report..."
        ]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, step in enumerate(progress_steps):
            status_text.text(step)
            progress_bar.progress((i + 1) / len(progress_steps))
            time.sleep(0.5)  # Simulate processing time
        
        try:
            # Run the actual CrewAI analysis with API key
            results = run_crew_analysis(df, analysis_options)
            
            if results:
                # Format results for display
                formatted_results = format_results_for_display(results)
                status_text.text("✅ Analysis completed successfully!")
                return formatted_results
            else:
                # Fallback to sample analysis if CrewAI fails
                st.warning("CrewAI analysis with Gemini API unavailable. Generating sample analysis...")
                status_text.text("⚠️ Using fallback analysis...")
                return generate_fallback_analysis(df)
                
        except Exception as e:
            st.warning(f"Gemini API analysis failed: {str(e)}. Generating sample analysis...")
            status_text.text("⚠️ Using fallback analysis...")
            return generate_fallback_analysis(df)

def generate_fallback_analysis(df):
    """Generate fallback analysis when CrewAI is not available"""
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    # Generate basic insights
    insights = [
        f"Dataset contains {len(df):,} records across {len(df.columns)} columns",
        f"Found {len(numeric_cols)} numeric and {len(categorical_cols)} categorical columns",
        f"Data completeness: {((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}%"
    ]
    
    if len(numeric_cols) > 0:
        insights.append(f"Numeric columns show varying distributions and ranges")
    
    # Generate recommendations
    recommendations = [
        "Implement regular data quality monitoring",
        "Consider data validation processes for missing values",
        "Focus analysis on key performance indicators"
    ]
    
    if df.isnull().sum().sum() > 0:
        recommendations.append("Address missing data through imputation or collection improvements")
    
    # Generate summary statistics
    if len(numeric_cols) > 0:
        summary_stats = df[numeric_cols].describe()
    else:
        # Create a basic summary for non-numeric data
        summary_stats = pd.DataFrame({
            'Total Records': [len(df)],
            'Total Columns': [len(df.columns)],
            'Missing Values': [df.isnull().sum().sum()],
            'Numeric Columns': [len(numeric_cols)],
            'Categorical Columns': [len(categorical_cols)]
        })
    
    # Generate visualizations
    visualizations = generate_sample_charts(df)
    
    # Generate report
    report = generate_sample_report(df)
    
    return {
        'insights': insights,
        'recommendations': recommendations,
        'summary_stats': summary_stats,
        'visualizations': visualizations,
        'report': report
    }

def generate_sample_charts(df):
    """Generate sample charts from the data"""
    charts = {}
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) >= 2:
        # Correlation heatmap
        corr_matrix = df[numeric_cols].corr()
        charts['correlation'] = px.imshow(
            corr_matrix,
            title="Correlation Matrix",
            color_continuous_scale="RdBu"
        )
        
        # Distribution plot
        charts['distribution'] = px.histogram(
            df, 
            x=numeric_cols[0],
            title=f"Distribution of {numeric_cols[0]}"
        )
        
        # Scatter plot if multiple numeric columns
        if len(numeric_cols) >= 2:
            charts['scatter'] = px.scatter(
                df,
                x=numeric_cols[0],
                y=numeric_cols[1],
                title=f"{numeric_cols[0]} vs {numeric_cols[1]}"
            )
    
    return charts

def generate_sample_report(df):
    """Generate a sample report"""
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    report = f"""
# Data Analysis Report

## Executive Summary
This report provides a comprehensive analysis of the uploaded dataset containing {len(df)} records and {len(df.columns)} columns.

## Data Overview
- **Total Records**: {len(df):,}
- **Numeric Columns**: {len(numeric_cols)}
- **Categorical Columns**: {len(categorical_cols)}
- **Missing Data**: {df.isnull().sum().sum()} values

## Key Findings
1. **Data Quality**: The dataset shows {'good' if df.isnull().sum().sum() < len(df) * 0.1 else 'moderate'} data quality
2. **Distribution**: Data shows {'normal' if len(numeric_cols) > 0 else 'non-numeric'} distribution patterns
3. **Completeness**: {((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}% data completeness

## Recommendations
- Regular data quality monitoring
- Focus on key performance indicators
- Implement data validation processes
"""
    return report

def generate_pdf_report(results):
    """Generate PDF report from analysis results"""
    if not PDF_AVAILABLE:
        return None
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Crew-AI Powered Data Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated on: {timestamp}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Key Insights Section
        story.append(Paragraph("Key Insights", styles['Heading2']))
        if 'insights' in results and results['insights']:
            for i, insight in enumerate(results['insights'], 1):
                story.append(Paragraph(f"{i}. {insight}", styles['Normal']))
        else:
            story.append(Paragraph("No insights available.", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary Statistics Section
        story.append(Paragraph("Summary Statistics", styles['Heading2']))
        if 'summary_stats' in results and results['summary_stats'] is not None:
            try:
                stats_df = results['summary_stats']
                # Check if DataFrame has data
                if not stats_df.empty and len(stats_df.columns) > 0:
                    # Convert DataFrame to table format
                    stats_data = [stats_df.columns.tolist()]
                    for _, row in stats_df.iterrows():
                        stats_data.append([str(val) for val in row.tolist()])
                    
                    # Only create table if we have both headers and data
                    if len(stats_data) > 1 and len(stats_data[0]) > 0:
                        table = Table(stats_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 12),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(table)
                    else:
                        story.append(Paragraph("No statistical data available.", styles['Normal']))
                else:
                    story.append(Paragraph("No statistical data available.", styles['Normal']))
            except Exception as e:
                story.append(Paragraph(f"Error displaying statistics: {str(e)}", styles['Normal']))
        else:
            story.append(Paragraph("No statistical data available.", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Recommendations Section
        story.append(Paragraph("Recommendations", styles['Heading2']))
        if 'recommendations' in results and results['recommendations']:
            for i, rec in enumerate(results['recommendations'], 1):
                story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
        else:
            story.append(Paragraph("No recommendations available.", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Full Report Text
        if 'report' in results and results['report']:
            story.append(Paragraph("Detailed Analysis", styles['Heading2']))
            # Split report into paragraphs
            report_lines = results['report'].split('\n')
            for line in report_lines:
                if line.strip():
                    if line.startswith('#'):
                        # Handle markdown headers
                        level = len(line) - len(line.lstrip('#'))
                        text = line.lstrip('# ').strip()
                        if level == 1:
                            story.append(Paragraph(text, styles['Heading1']))
                        elif level == 2:
                            story.append(Paragraph(text, styles['Heading2']))
                        else:
                            story.append(Paragraph(text, styles['Heading3']))
                    else:
                        story.append(Paragraph(line, styles['Normal']))
                    story.append(Spacer(1, 6))
        else:
            story.append(Paragraph("Detailed Analysis", styles['Heading2']))
            story.append(Paragraph("No detailed analysis available.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None

def display_results(results):
    """Display analysis results"""
    st.markdown("## 📊 Analysis Results")
    
    # Key Insights
    st.markdown("### 💡 Key Insights")
    insights_container = st.container()
    with insights_container:
        for i, insight in enumerate(results['insights'], 1):
            st.markdown(f"**{i}.** {insight}")
    
    # Visualizations
    if results['visualizations']:
        st.markdown("### 📈 Visualizations")
        
        for chart_name, chart in results['visualizations'].items():
            st.plotly_chart(chart, use_container_width=True)
    
    # Summary Statistics
    st.markdown("### 📋 Summary Statistics")
    st.dataframe(results['summary_stats'], use_container_width=True)
    
    # Recommendations
    st.markdown("### 🎯 Recommendations")
    for i, rec in enumerate(results['recommendations'], 1):
        st.markdown(f"**{i}.** {rec}")

def create_download_section(results):
    """Create download section for reports"""
    st.markdown("### 📥 Download Reports")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Download full report as text
        if st.download_button(
            label="📄 Download Report (TXT)",
            data=results['report'],
            file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        ):
            st.success("Report downloaded!")
    
    with col2:
        # Download summary statistics as CSV
        csv_buffer = StringIO()
        results['summary_stats'].to_csv(csv_buffer)
        if st.download_button(
            label="📊 Download Stats (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"summary_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        ):
            st.success("Statistics downloaded!")
    
    with col3:
        # Download insights as JSON
        insights_data = {
            'insights': results['insights'],
            'recommendations': results['recommendations'],
            'timestamp': datetime.now().isoformat()
        }
        if st.download_button(
            label="💡 Download Insights (JSON)",
            data=json.dumps(insights_data, indent=2),
            file_name=f"insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        ):
            st.success("Insights downloaded!")
    
    with col4:
        # Download PDF report
        if PDF_AVAILABLE:
            pdf_data = generate_pdf_report(results)
            if pdf_data:
                if st.download_button(
                    label="📑 Download PDF Report",
                    data=pdf_data,
                    file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                ):
                    st.success("PDF Report downloaded!")
            else:
                st.error("Failed to generate PDF")
        else:
            st.info("📑 PDF Download\n\nInstall reportlab: `pip install reportlab`")

def main():
    """Main application function"""
    initialize_session_state()
    display_header()
    
    # Create sidebar and get inputs
    uploaded_file, analysis_depth, chart_types, api_key = create_sidebar()
    
    if uploaded_file is not None:
        try:
            # Read and validate data
            df = pd.read_csv(uploaded_file)
            issues = validate_csv_data(df)
            
            if issues:
                st.error("Data Validation Issues:")
                for issue in issues:
                    st.error(f"• {issue}")
                return
            
            st.session_state.uploaded_data = df
            
            # Display data preview
            display_data_preview(df)
            
            # Analysis button with API key check
            analysis_button_disabled = not api_key or len(api_key) <= 20
            
            if analysis_button_disabled:
                st.warning("🔑 Please enter a valid Gemini API Key in the sidebar to enable AI analysis")
            
            if st.button(
                "🚀 Start AI Analysis", 
                type="primary", 
                use_container_width=True,
                disabled=analysis_button_disabled
            ):
                with st.spinner("Initializing AI Agents..."):
                    results = run_crew_analysis_with_ui(df, analysis_depth, chart_types, api_key)
                    
                    if results:
                        st.session_state.analysis_results = results
                        st.session_state.analysis_complete = True
                        st.success("Analysis completed successfully!")
                        st.rerun()
            
            # Display results if analysis is complete
            if st.session_state.analysis_complete and st.session_state.analysis_results:
                display_results(st.session_state.analysis_results)
                create_download_section(st.session_state.analysis_results)
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.info("Please check your CSV file format and try again.")
    
    else:
        display_upload_section()
        
        # Show API key requirement prominently
        if not st.session_state.get('gemini_api_key'):
            st.info("""
            ### 🔑 API Key Required
            
            To use the AI-powered analysis features, you'll need a **Gemini API Key**:
            
            1. 📡 **Get your free API key**: [Google AI Studio](https://aistudio.google.com/u/3/apikey)
            2. 🔑 **Enter it in the sidebar** under "AI Configuration"
            3. 📊 **Upload your CSV** and start analyzing!
            
            The free tier includes generous limits for most analysis needs.
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <style>
    body[data-theme="light"] .custom-footer {
        color: #666;
    }
    body[data-theme="dark"] .custom-footer {
        color: #ccc;
    }
    </style>

    <div class="custom-footer" style="text-align: center;">
        With 💝 from Akshay
    </div>
    <div class="custom-footer" style="text-align: center;">
        Powered by CrewAI Agents • Built with Streamlit • Enhanced with Gemini AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()