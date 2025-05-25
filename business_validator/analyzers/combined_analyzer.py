"""
Combined analysis of multiple data sources for business idea validation.
"""
import logging
from typing import List, Dict, Any

from SimpleLLM.language.llm import LLM, LLMProvider
from SimpleLLM.language.llm_addons import generate_basic_pydantic_json_model
from SimpleLLM.webtools.web_search import WebSearchClient

from business_validator.models import CombinedAnalysis, PlatformInsight

# Use the same LLM instance as in keyword_generator
from business_validator.analyzers.keyword_generator import llm_instance

# Initialize WebSearchClient for broader platform insights
web_search_client = WebSearchClient()

def gather_web_platform_insights(business_idea: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
    """
    Gather insights from broader web search about the business idea.
    
    Args:
        business_idea: The business idea being validated
        keywords: Optional list of keywords related to the business idea
        
    Returns:
        List of search results with platform insights
    """
    logging.info("Gathering web platform insights...")
    
    search_results = []
    search_queries = []
    
    # Create search queries based on business idea and keywords
    base_queries = [
        f'"{business_idea}" market research insights',
        f'"{business_idea}" customer problems pain points',
        f'"{business_idea}" competition analysis',
        f'"{business_idea}" market opportunity trends'
    ]
    
    search_queries.extend(base_queries)
    
    # Add keyword-based queries if keywords are provided
    if keywords:
        for keyword in keywords[:2]:  # Limit to first 2 keywords to avoid too many searches
            search_queries.extend([
                f'"{keyword}" market discussions forums',
                f'"{keyword}" customer feedback reviews'
            ])
    
    # Perform web searches
    try:
        for query in search_queries[:6]:  # Limit total searches to 6
            logging.info(f"Searching web for: {query}")
            results = web_search_client.search(query, num_results=2)
            for result in results:
                result['search_query'] = query
                search_results.append(result)
        
        logging.info(f"Gathered {len(search_results)} web search results")
        
    except Exception as e:
        logging.error(f"Error gathering web search insights: {str(e)}")
        # Continue with empty results if search fails
    
    return search_results

def generate_final_analysis(
    business_idea: str,
    hn_analyses: List[Dict[str, Any]],
    reddit_analyses: List[Dict[str, Any]],
    keywords: List[str] = None
) -> CombinedAnalysis:
    """
    Generate a final combined analysis from all data sources including web search.
    
    Args:
        business_idea: The business idea being validated
        hn_analyses: List of HackerNews post analyses
        reddit_analyses: List of Reddit post analyses
        keywords: Optional list of keywords for enhanced web search
        
    Returns:
        CombinedAnalysis object with the final analysis
    """
    # Initialize empty lists if none are provided
    if hn_analyses is None:
        hn_analyses = []
    if reddit_analyses is None:
        reddit_analyses = []
    
    # Gather web search insights for broader platform analysis
    web_insights = gather_web_platform_insights(business_idea, keywords)
    
    # Prepare summary of HackerNews data
    hn_summary = ""
    if hn_analyses:
        hn_summary = "HackerNews Data:\\n"
        for i, hn_analysis in enumerate(hn_analyses, 1):
            post = hn_analysis["post"]
            analysis = hn_analysis["analysis"]
            
            if not analysis.get("relevant", False):
                continue
                
            title = post.get("title", "Untitled")
            hn_summary += f"Post {i}: {title}\\n"
            hn_summary += f"- Pain points: {', '.join(analysis.get('pain_points', []))}\\n"
            hn_summary += f"- Solutions: {', '.join(analysis.get('solutions_mentioned', []))}\\n"
            hn_summary += f"- Market signals: {', '.join(analysis.get('market_signals', []))}\\n"
            hn_summary += f"- Sentiment: {analysis.get('sentiment', 'neutral')}\\n"
            hn_summary += f"- Engagement: {analysis.get('engagement_score', 0)}/10\\n\\n"
    
    # Prepare summary of Reddit data
    reddit_summary = ""
    if reddit_analyses:
        reddit_summary = "Reddit Data:\\n"
        for i, reddit_analysis in enumerate(reddit_analyses, 1):
            post = reddit_analysis["post"]
            analysis = reddit_analysis["analysis"]
            
            if not analysis.get("relevant", False):
                continue
                
            title = post.get("title", "Untitled")
            subreddit = post.get("subreddit", "Unknown")
            reddit_summary += f"Post {i}: {title} (r/{subreddit})\\n"
            reddit_summary += f"- Pain points: {', '.join(analysis.get('pain_points', []))}\\n"
            reddit_summary += f"- Solutions: {', '.join(analysis.get('solutions_mentioned', []))}\\n"
            reddit_summary += f"- Market signals: {', '.join(analysis.get('market_signals', []))}\\n"
            reddit_summary += f"- Sentiment: {analysis.get('sentiment', 'neutral')}\\n"
            reddit_summary += f"- Engagement: {analysis.get('engagement_score', 0)}/10\\n"
            reddit_summary += f"- Subreddit context: {analysis.get('subreddit_context', '')}\\n\\n"

    # Prepare summary of web search insights
    web_summary = ""
    if web_insights:
        web_summary = "Web Search Insights Data:\\n"
        for i, result in enumerate(web_insights, 1):
            title = result.get("title", "Untitled")
            url = result.get("link", result.get("url", ""))
            snippet = result.get("snippet", result.get("description", ""))
            query = result.get("search_query", "")
            web_summary += f"Result {i}: {title}\\n"
            web_summary += f"- URL: {url}\\n"
            web_summary += f"- Search Query: {query}\\n"
            web_summary += f"- Content: {snippet}\\n\\n"

    # Basic escaping for summaries to be included in the prompt
    # This helps prevent characters in the summaries from breaking the LLM's interpretation of the prompt structure.
    safe_hn_summary = hn_summary.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    safe_reddit_summary = reddit_summary.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    safe_web_summary = web_summary.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

    prompt = (
        f"""Analyze the following data collected about this business idea:

BUSINESS IDEA: {business_idea}

{safe_hn_summary}

{safe_reddit_summary}

{safe_web_summary}

Based on all this data, provide a comprehensive market validation analysis.
You MUST return ONLY a single, valid JSON object as your response. Do not include any explanatory text, comments, or markdown formatting before or after the JSON object.
The JSON object must strictly follow this structure:
{{
  "overall_score": <integer_between_0_and_100>,
  "market_validation_summary": "<string_summary_text>",
  "key_pain_points": ["<string_point1>", "<string_point2>", ...],
  "existing_solutions": ["<string_solution1>", "<string_solution2>", ...],
  "market_opportunities": ["<string_opportunity1>", "<string_opportunity2>", ...],
  "platform_insights": [
    {{
      "platform": "HackerNews",
      "insights": "<string_insights_text_for_HN>"
    }},
    {{
      "platform": "Reddit",
      "insights": "<string_insights_text_for_Reddit>"
    }},
    {{
      "platform": "Web Search",
      "insights": "<string_insights_text_for_broader_web_analysis>"
    }}
  ],
  "recommendations": ["<string_recommendation1>", "<string_recommendation2>", ...]
}}

IMPORTANT JSON FORMATTING RULES:
- The entire response must be a single JSON object starting with `{{` and ending with `}}`.
- All keys and string values must be enclosed in double quotes (e.g., "key": "value").
- Escape any double quotes within string values using a backslash (e.g., "description": "This is a \"quoted\" example.").
- Escape any backslashes within string values using another backslash (e.g., "path": "C:\\folder\\file").
- Ensure all commas, colons, curly braces, and square brackets are correctly placed according to standard JSON syntax.
- Do not use trailing commas after the last element in an array or the last property in an object.
- The `overall_score` must be an integer (e.g., 75), not a string.
- All text fields (like summaries, insights, points, solutions, opportunities, recommendations) should be concise yet informative. If a list is empty, use an empty array `[]`.
Be thorough in your analysis.
"""
    )
    
    try:
        logging.info(f"Attempting to generate final analysis for: {business_idea}")
        # Limit logging of potentially very long prompts in production, but useful for debugging
        # logging.debug(f"Prompt for LLM: {prompt}")
        if len(prompt) > 1000: # Log a snippet if too long
             logging.debug(f"Prompt for LLM (first 1000 chars): {prompt[:1000]}...")
        else:
            logging.debug(f"Prompt for LLM: {prompt}")

        analysis = generate_basic_pydantic_json_model(
            model_class=CombinedAnalysis,
            llm_instance=llm_instance,
            prompt=prompt
        )
        logging.info("Successfully generated final analysis.")
        return analysis
    except Exception as e:
        logging.error(f"Error generating final analysis with LLM: {e}. Falling back to default CombinedAnalysis object.")
        
        # Fallback to a default, Pydantic-valid CombinedAnalysis object
        # This ensures the function always returns the expected type, preventing downstream Pydantic errors.
        return CombinedAnalysis(
            overall_score=0,
            market_validation_summary="Failed to generate analysis due to an internal LLM error. The LLM did not return a valid JSON response that could be parsed.",
            key_pain_points=["Analysis failed or not performed"],
            existing_solutions=["Analysis failed or not performed"],
            market_opportunities=["Analysis failed or not performed"],
            platform_insights=[
                PlatformInsight(platform="HackerNews", insights="Analysis failed, no data processed, or LLM response was invalid."),
                PlatformInsight(platform="Reddit", insights="Analysis failed, no data processed, or LLM response was invalid."),
                PlatformInsight(platform="Web Search", insights="Analysis failed, no data processed, or LLM response was invalid.")
            ],
            recommendations=["Try again. If the problem persists, please check the application logs for more details on the LLM failure."]
        )
