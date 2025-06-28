from crewai import Agent

class ReportWriterAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Report Writer",
            goal="Create comprehensive business reports",
            backstory="Technical writer specializing in data-driven reports",
            verbose=True
        )