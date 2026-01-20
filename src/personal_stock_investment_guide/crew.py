from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage


# -------------------------
# Pydantic Outputs
# -------------------------

class SectorCandidate(BaseModel):
    name: str = Field(description="Sector name in Morocco context")
    rank: int = Field(description="Rank (1 = best)")
    thesis: str = Field(description="Long-term investment thesis (10–15y) in Morocco")
    key_drivers: List[str] = Field(description="Structural tailwinds/drivers")
    key_risks: List[str] = Field(description="Main risks and what could break the thesis")
    sources: List[str] = Field(description="Cited links used for this sector")

class SectorList(BaseModel):
    sectors: List[SectorCandidate] = Field(description="Ranked list of top sectors")

class ShariaApprovedSector(BaseModel):
    name: str = Field(description="Sector name")
    approved: bool = Field(description="Whether sector is Sharia-compliant by activity")
    notes: str = Field(description="Screening notes, including any caveats/uncertainties")
    sources: List[str] = Field(default_factory=list, description="Links if used")

class ShariaApprovedSectorList(BaseModel):
    sectors: List[ShariaApprovedSector] = Field(description="Sharia screening results for sectors")

class CompanyCandidate(BaseModel):
    name: str = Field(description="Company name")
    ticker: Optional[str] = Field(default=None, description="Ticker symbol if applicable")
    sector: str = Field(description="Mapped sector from the approved list")
    rationale: str = Field(description="Why this company belongs on the shortlist")
    sources: List[str] = Field(description="Links supporting the shortlist inclusion")

class CompanyShortlist(BaseModel):
    companies: List[CompanyCandidate] = Field(description="Shortlisted Moroccan listed companies")

class CompanyDeepResearch(BaseModel):
    name: str = Field(description="Company name")
    ticker: Optional[str] = Field(default=None, description="Ticker symbol if applicable")
    sector: str = Field(description="Sector")
    business_model: str = Field(description="How the company makes money; key revenue drivers")
    competitive_position: str = Field(description="Market position, moat, competitors (Morocco context)")
    vision_and_strategy: str = Field(description="Company vision/strategy; key stated objectives")
    vision_vs_execution: str = Field(description="How well the company historically delivered vs its stated vision/plans")
    financial_trends: str = Field(description="5–10y trend summary: revenue/profitability/leverage/cash/dividends where possible")
    governance_and_ownership: str = Field(description="Governance, ownership structure, any red flags")
    key_risks: List[str] = Field(description="Key long-term risks")
    long_term_outlook: str = Field(description="Long-term outlook (10–15y) with assumptions")
    trustworthiness_assessment: str = Field(description="Evidence-based qualitative trust assessment")
    sources: List[str] = Field(description="Primary + credible sources used (links)")

class CompanyDeepResearchList(BaseModel):
    research: List[CompanyDeepResearch] = Field(description="Deep research for all companies")


@CrewBase
class MoroccoInvestmentGuideCrew:
    """Morocco long-term investing guide crew (Sharia-aware)."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # -------------------------
    # Agents
    # -------------------------
    @agent
    def macro_sector_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['macro_sector_strategist'],
            tools=[SerperDevTool()],
            memory=True
        )

    @agent
    def sharia_screening_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['sharia_screening_analyst'],
            tools=[SerperDevTool()],
            memory=True
        )

    @agent
    def morocco_equity_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['morocco_equity_researcher'],
            tools=[SerperDevTool()],
            memory=True
        )

    @agent
    def portfolio_guide_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['portfolio_guide_writer'],
            tools=[SerperDevTool()],
            memory=True
        )

    @agent
    def investment_report_writer(self) -> Agent:
         return Agent(
            config=self.agents_config['investment_report_writer'],
            tools=[SerperDevTool()],
            memory=True
        )

    # -------------------------
    # Tasks
    # -------------------------
    @task
    def find_top_morocco_sectors(self) -> Task:
        return Task(
            config=self.tasks_config['find_top_morocco_sectors'],
            output_pydantic=SectorList,
        )

    @task
    def screen_sectors_for_sharia(self) -> Task:
        return Task(
            config=self.tasks_config['screen_sectors_for_sharia'],
            output_pydantic=ShariaApprovedSectorList,
        )

    @task
    def shortlist_listed_companies_ma(self) -> Task:
        return Task(
            config=self.tasks_config['shortlist_listed_companies_ma'],
            output_pydantic=CompanyShortlist,
        )

    @task
    def deep_research_companies_ma(self) -> Task:
        return Task(
            config=self.tasks_config['deep_research_companies_ma'],
            output_pydantic=CompanyDeepResearchList,
        )

    @task
    def build_long_term_investing_guide_ma(self) -> Task:
        return Task(
            config=self.tasks_config['build_long_term_investing_guide_ma'],
        )
    @task
    def write_professional_investment_report(self) -> Task:
        return Task(
            config=self.tasks_config['write_professional_investment_report'],
        )


    # -------------------------
    # Crew
    # -------------------------
    @crew
    def crew(self) -> Crew:
        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,
            embedder={
                "provider": "ollama",
                "config": {
                    "model": "nomic-embed-text"
                }
            },
            long_term_memory=LongTermMemory(
                storage=LTMSQLiteStorage(db_path="./memory/long_term_memory_storage.db")
            ),
        )

