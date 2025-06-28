from crewai import Agent

class InsightAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Business Intelligence Analyst",
            goal="Generate actionable business insights from data",
            backstory="Experienced business analyst with domain expertise",
            verbose=True
        )