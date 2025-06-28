# 📊 CrewAI-Powered Business Intelligence Dashboard 📈
AI-powered business dashboard that uses CrewAI agents to analyze data and generate insights automatically.

## Demo ▶️

https://github.com/user-attachments/assets/f699f23f-9cef-4cb3-b7fc-3e3f2f2bb4ee

## Problem We Solve 🚨

**Traditional BI tools are expensive and complex:**
- Require specialized analysts to interpret data
- Take weeks to generate meaningful reports
- Cost thousands of dollars in licensing fees
- Need technical expertise to set up dashboards

## Our Solution 🚀

**AI agents that work like a team of analysts:**
- **Data Analyst Agent** - Automatically finds patterns in your data
- **Business Intelligence Agent** - Generates insights and recommendations
- **Report Writer Agent** - Creates professional reports in minutes
- **Visualization Agent** - Builds interactive charts and dashboards

## Impact & Benefits 🖥️

✅ **Save Time**: Get insights in minutes, not weeks  
✅ **Save Money**: No expensive BI software licenses needed  
✅ **No Expertise Required**: AI agents do the complex analysis  
✅ **24/7 Availability**: Automated reporting works around the clock  
✅ **Scalable**: Handles small datasets to enterprise-level data  

**Real Results:**
- Reduce report generation time by 90%
- Cut BI costs by up to 80%
- Enable data-driven decisions for non-technical users

## What it does

- Analyzes your business data using AI agents
- Creates interactive charts and dashboards
- Generates automated reports
- Provides real-time business insights

## Quick Start

### Option 1: Streamlit Cloud (Deployed)

https://crewai-powered-bi-dashboard.streamlit.app/

### Option 2: Local Server

### 1. Install 

```bash
git clone https://github.com/Akshay-66/crewai-powered-bi-dashboard.git
cd crewai-powered-bi-dashboard
pip install -r requirements.txt
```

### 2. Setup

Create `.env` file:
```env
MODEL=gemini/gemini-2.0-flash-001
GEMINI_API_KEY="GEMINI_API_KEY"
```

### 3. Run

```bash
streamlit run app.py
```

App will open automatically in your browser at http://localhost:8501

### Option 3: Docker

```bash
docker build -t crewai-dashboard .
docker run -p 8501:8501 --env-file .env crewai-dashboard
```
Note: Make sure your Dockerfile exposes port 8501 and runs Streamlit properly

## Need Help?

- Check the Streamlit logs in terminal if something breaks
- Make sure your API keys are correct in secrets (.env / dashboard sidebar)
- Ensure port 8501 is available (Streamlit default) for local deployment
- For Streamlit Cloud: Check the app logs in the dashboard
