"""
Pydantic models for business validator.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class HNPostAnalysis(BaseModel):
    """Analysis of a HackerNews post."""
    relevant: bool = Field(..., description="Whether this post is relevant to the business idea")
    pain_points: List[str] = Field([], description="Pain points identified in the post")
    solutions_mentioned: List[str] = Field([], description="Solutions mentioned in the post")
    market_signals: List[str] = Field([], description="Market signals identified in the post")
    sentiment: str = Field(..., description="Overall sentiment: positive, negative, or neutral")
    engagement_score: int = Field(..., description="A score from 1-10 indicating user engagement with the topic")


class RedditPostAnalysis(BaseModel):
    """Analysis of a Reddit post and its comments."""
    relevant: bool = Field(..., description="Whether this post is relevant to the business idea")
    pain_points: List[str] = Field([], description="Pain points identified in the post or comments")
    solutions_mentioned: List[str] = Field([], description="Solutions mentioned in the post or comments")
    market_signals: List[str] = Field([], description="Market signals identified in the post or comments")
    sentiment: str = Field(..., description="Overall sentiment: positive, negative, or neutral")
    engagement_score: int = Field(..., description="A score from 1-10 indicating user engagement with the topic")
    subreddit_context: str = Field(..., description="Context about the relevance of this subreddit to the business idea")


class PlatformInsight(BaseModel):
    """Platform-specific insights."""
    platform: str = Field(..., description="Name of the platform (e.g., 'HackerNews', 'Reddit')")
    insights: str = Field(..., description="Insights specific to this platform")


class CombinedAnalysis(BaseModel):
    """Combined analysis of all data sources."""
    overall_score: int = Field(..., description="Overall validation score from 0-100")
    market_validation_summary: str = Field(..., description="Summary of market validation findings")
    key_pain_points: List[str] = Field([], description="Key pain points discovered across all sources")
    existing_solutions: List[str] = Field([], description="Existing solutions found across all sources")
    market_opportunities: List[str] = Field([], description="Market opportunities identified across all sources")
    platform_insights: List[PlatformInsight] = Field([], description="Platform-specific insights")
    recommendations: List[str] = Field([], description="Recommendations based on the analysis")
