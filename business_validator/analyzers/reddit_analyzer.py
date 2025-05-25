"""
Reddit post analysis for business idea validation.
"""
import logging
from typing import Dict, List

from SimpleLLM.language.llm import LLM, LLMProvider
from SimpleLLM.language.llm_addons import generate_basic_pydantic_json_model

from business_validator.models import RedditPostAnalysis

# Use the same LLM instance as in keyword_generator
from business_validator.analyzers.keyword_generator import llm_instance

def analyze_reddit_post(post: dict, comments: List[dict], business_idea: str) -> RedditPostAnalysis:
    """
    Analyze a Reddit post for business validation insights.
    
    Args:
        post: Dictionary containing post information
        comments: List of dictionaries containing comment information
        business_idea: The business idea being validated
        
    Returns:
        RedditPostAnalysis object containing the analysis
    """
    # Combine post and comments into a single content string
    post_title = post.get("title", "")
    post_content = post.get("content", "")
    subreddit = post.get("subreddit", "")
    votes = post.get("votes", 0)
    
    combined_content = f"Title: {post_title}\n\nContent: {post_content}\n\nSubreddit: {subreddit}, Votes: {votes}\n\n"
    
    if comments:
        combined_content += "Comments:\n"
        for comment in comments[:10]:  # Limit to top 10 comments
            author = comment.get("author", "Unknown")
            text = comment.get("text", "")
            score = comment.get("score", 0)
            combined_content += f"Comment by {author} (Score: {score}):\n{text}\n\n"
    
    # Create the analysis prompt
    prompt = (
        f"Analyze this Reddit post content for insights related to the business idea:\n\n"
        f"BUSINESS IDEA: {business_idea}\n\n"
        f"POST CONTENT:\n{combined_content}\n\n"
        f"Respond with the following analysis in JSON format:\n"
        f"- Is the post relevant to our business idea? (true/false)\n"
        f"- What pain points are mentioned?\n"
        f"- What solutions are mentioned?\n"
        f"- What market signals can we extract?\n"
        f"- What is the overall sentiment? (positive/negative/neutral)\n"
        f"- Rate engagement score 1-10 based on votes, comments and discussion quality\n"
        f"- Provide context about the subreddit relevance to our business idea\n\n"
        f"Focus on extracting actionable insights for business validation."
    )

    try:
        analysis = generate_basic_pydantic_json_model(
            model_class=RedditPostAnalysis,
            llm_instance=llm_instance,
            prompt=prompt
        )

        return analysis
    except Exception as e:
        logging.error(f"Error analyzing Reddit post: {e}")
        # Return a default analysis if generation fails
        return RedditPostAnalysis(
            relevant=False,
            pain_points=["Analysis failed"],
            solutions_mentioned=["Analysis failed"],
            market_signals=["Analysis failed"],
            sentiment="neutral",
            engagement_score=0,
            subreddit_context="Analysis failed"
        )
