from pydantic import BaseModel, Field
from typing import Optional

class AgentState(BaseModel):
    job_url: str
    resume_path: str
    job_description: Optional[str] = None
    resume_text: Optional[str] = None
    skill_gap_score: Optional[float] = None
    missing_skills: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    gap_analysis: dict = Field(default_factory=dict)
    tailored_resume: Optional[str] = None
    cover_letter: Optional[str] = None
    human_approved: bool = False
    submit_status: Optional[str] = None