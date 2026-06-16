from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class GitHubUser(BaseModel):
    """Data blueprint encapsulating profile properties of a target entity."""
    id: int
    login: str
    avatar_url: str
    html_url: str
    type: str

class Repository(BaseModel):
    """Data blueprint encapsulating statistical repository markers."""
    id: int
    name: str
    full_name: str
    private: bool
    owner: GitHubUser
    description: Optional[str] = None
    html_url: str
    
    # Aliased field mapping handles conversions between snake_case and JSON keys securely
    stargazers_count: int = Field(..., alias="stargazers_count")
    forks_count: int
    open_issues_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True