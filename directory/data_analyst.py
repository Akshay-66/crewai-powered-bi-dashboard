from crewai import Agent
from crewai.tools import BaseTool
from .tools import csv_summary_tool
class DataAnalystAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Data Analyst",
            goal="Analyze CSV data and provide statistical insights",
            backstory="Expert in statistical analysis and data quality assessment",
            tools=[csv_summary_tool()],
            verbose=True
        )