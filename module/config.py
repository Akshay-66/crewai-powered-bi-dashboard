"""
Configuration file for AI-Powered BI Dashboard
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Streamlit Configuration
    STREAMLIT_PORT = os.getenv('STREAMLIT_SERVER_PORT', 8501)
    STREAMLIT_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost')
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", '')
    
    # CrewAI Configuration
    CREW_VERBOSE = os.getenv('CREW_VERBOSE', 'True').lower() == 'true'
    CREW_MEMORY = os.getenv('CREW_MEMORY', 'True').lower() == 'true'
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 200))
    ALLOWED_FILE_TYPES = ['csv']
    
    # Analysis Configuration
    DEFAULT_ANALYSIS_DEPTH = 'Basic'
    DEFAULT_CHART_TYPES = ['Line Charts', 'Bar Charts']
    MAX_VISUALIZATION_POINTS = int(os.getenv('MAX_VIZ_POINTS', 1000))
    
    # Performance Configuration
    ENABLE_CACHING = os.getenv('ENABLE_CACHING', 'True').lower() == 'true'
    CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', 3600))
    
    # UI Configuration
    APP_TITLE = "AI-Powered Business Intelligence Dashboard"
    APP_ICON = "📊"
    SIDEBAR_STATE = "expanded"
    
    # Report Configuration
    REPORT_FORMATS = ['txt', 'csv', 'json', 'pdf']
    DEFAULT_REPORT_FORMAT = 'txt'
    
    # Chart Configuration
    CHART_THEMES = ['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 'seaborn']
    DEFAULT_CHART_THEME = 'plotly'
    
    # Data Processing Configuration
    SAMPLE_SIZE_LARGE_FILES = int(os.getenv('SAMPLE_SIZE', 10000))
    CORRELATION_THRESHOLD = float(os.getenv('CORRELATION_THRESHOLD', 0.7))
    OUTLIER_METHOD = 'IQR'  # 'IQR' or 'zscore'
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        # Check required API keys for production
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            errors.append("No API keys configured. At least one AI provider key is recommended.")
        
        # Validate numeric settings
        if cls.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be positive")
        
        if cls.CORRELATION_THRESHOLD < 0 or cls.CORRELATION_THRESHOLD > 1:
            errors.append("CORRELATION_THRESHOLD must be between 0 and 1")
        
        return errors

# Analysis Templates
ANALYSIS_TEMPLATES = {
    'Basic': {
        'description': 'Quick overview with essential statistics',
        'includes': ['summary_stats', 'basic_insights', 'simple_charts'],
        'estimated_time': '1-2 minutes'
    },
    'Detailed': {
        'description': 'Comprehensive analysis with correlations',
        'includes': ['summary_stats', 'correlations', 'outliers', 'distributions', 'insights'],
        'estimated_time': '3-5 minutes'
    },
    'Comprehensive': {
        'description': 'Full analysis with predictive insights',
        'includes': ['all_features', 'advanced_analytics', 'predictions', 'recommendations'],
        'estimated_time': '5-10 minutes'
    }
}

# Chart Type Configurations
CHART_CONFIGS = {
    'Line Charts': {
        'suitable_for': ['time_series', 'trends', 'continuous_data'],
        'min_columns': 1,
        'data_types': ['numeric']
    },
    'Bar Charts': {
        'suitable_for': ['categorical_comparison', 'counts', 'frequencies'],
        'min_columns': 1,
        'data_types': ['categorical', 'numeric']
    },
    'Scatter Plots': {
        'suitable_for': ['relationships', 'correlations', 'patterns'],
        'min_columns': 2,
        'data_types': ['numeric']
    },
    'Heatmaps': {
        'suitable_for': ['correlations', 'matrix_data', 'patterns'],
        'min_columns': 2,
        'data_types': ['numeric']
    },
    'Distribution': {
        'suitable_for': ['data_distribution', 'normality', 'outliers'],
        'min_columns': 1,
        'data_types': ['numeric']
    }
}

# Error Messages
ERROR_MESSAGES = {
    'file_too_large': f"File size exceeds {Config.MAX_FILE_SIZE_MB}MB limit",
    'invalid_format': f"Invalid file format. Supported: {Config.ALLOWED_FILE_TYPES}",
    'empty_file': "Uploaded file is empty",
    'no_numeric_data': "No numeric columns found for analysis",
    'insufficient_data': "Insufficient data for meaningful analysis",
    'analysis_failed': "Analysis failed. Please try again or contact support"
}

# Success Messages
SUCCESS_MESSAGES = {
    'upload_success': "✅ File uploaded successfully",
    'analysis_complete': "✅ Analysis completed successfully",
    'report_generated': "✅ Report generated successfully",
    'download_ready': "✅ Download ready"
}

# UI Text and Labels
UI_TEXT = {
    'upload_instructions': """
    #### 📋 Instructions:
    1. **Upload CSV**: Select your business data file
    2. **AI Analysis**: Our agents will analyze your data
    3. **View Results**: Explore insights and visualizations
    4. **Download Report**: Get your complete analysis
    """,
    'data_requirements': """
    **Supported formats:** CSV files with headers
    **What you'll get:** Automated insights, visualizations, and comprehensive reports
    """,
    'footer_text': "Powered by CrewAI Agents • Built with Streamlit"
}

# Validation Rules
VALIDATION_RULES = {
    'min_rows': 10,
    'min_columns': 2,
    'max_missing_percentage': 80,  # Maximum percentage of missing data allowed
    'min_numeric_columns': 1
}

def get_config():
    """Get configuration instance with validation"""
    errors = Config.validate_config()
    if errors:
        print("Configuration warnings:")
        for error in errors:
            print(f"  - {error}")
    
    return Config

# Export configuration
config = get_config()