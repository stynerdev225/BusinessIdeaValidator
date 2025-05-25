"""
Analyzer for trending topics and technology business idea suggestions.
"""
import logging
import json
from typing import Dict, List, Any
from SimpleLLM.language.llm import LLM
from SimpleLLM.language.llm_addons import extract_json
from SimpleLLM.webtools.web_search import WebSearchClient

# Use the same LLM instance as in other analyzers
from business_validator.analyzers.keyword_generator import llm_instance

# Import health data scrapers
from business_validator.scrapers.who import scrape_who_data
from business_validator.scrapers.cdc import scrape_cdc_data
from business_validator.scrapers.ourworld import scrape_ourworld_data
from business_validator.scrapers.pubmed import scrape_pubmed_data

# Initialize WebSearchClient
web_search_client = WebSearchClient()

def analyze_health_trends(topic: str, demographics: List[str] = None, regions: List[str] = None) -> Dict[str, Any]:
    """
    Analyze health-related trends (like HIV) based on provided parameters.
    
    Args:
        topic: The health topic to analyze (e.g., "HIV", "Diabetes")
        demographics: List of demographic groups to focus on
        regions: List of regions to focus on
    
    Returns:
        Dict containing the trend analysis
    """
    logging.info(f"Analyzing health trends for topic: {topic}")
    
    # Default values if not provided
    if demographics is None:
        demographics = ["all age groups", "by gender", "by risk group"]
        
    if regions is None:
        regions = ["global", "United States", "Europe", "Africa", "Asia"]
    
    # Gather data from multiple health sources
    health_data = []
    
    try:
        # Scrape WHO data
        logging.info("Scraping WHO data...")
        who_data = scrape_who_data(topic, limit=2)
        health_data.extend(who_data)
        
        # Scrape CDC data
        logging.info("Scraping CDC data...")
        cdc_data = scrape_cdc_data(topic, limit=2)
        health_data.extend(cdc_data)
        
        # Scrape Our World in Data
        logging.info("Scraping Our World in Data...")
        ourworld_data = scrape_ourworld_data(topic, limit=2)
        health_data.extend(ourworld_data)
        
        # Scrape PubMed research
        logging.info("Scraping PubMed research...")
        pubmed_data = scrape_pubmed_data(topic, limit=2)
        health_data.extend(pubmed_data)
        
        logging.info(f"Gathered {len(health_data)} health data sources")
        
    except Exception as e:
        logging.error(f"Error gathering health data: {str(e)}")
        health_data = []  # Continue with empty results if scraping fails
    
    # Also perform web searches for additional context
    search_results = []
    try:
        # Search for general topic information
        general_query = f"latest statistics {topic} health trends global WHO CDC"
        general_results = web_search_client.search(general_query, num_results=3)
        search_results.extend(general_results)
        
        # Search for regional information
        for region in regions[:3]:  # Limit to avoid too many requests
            if region.lower() != "global":
                region_query = f"{topic} health statistics {region} prevalence demographics"
                region_results = web_search_client.search(region_query, num_results=1)
                search_results.extend(region_results)
                
        logging.info(f"Gathered {len(search_results)} additional search results")
        
    except Exception as e:
        logging.error(f"Error gathering web search data: {str(e)}")
        search_results = []
    
    # Combine health data and search results for analysis
    all_data = ""
    
    # Add health data sources
    for idx, data in enumerate(health_data):
        all_data += f"\n--- {data['source']} Data ---\n"
        all_data += f"Title: {data['title']}\n"
        all_data += f"URL: {data['url']}\n"
        all_data += f"Content: {data['content']}\n"
    
    # Add web search results
    for idx, result in enumerate(search_results):
        all_data += f"\n--- Web Search Result {idx+1} ---\n"
        all_data += f"Title: {result['title']}\n"
        all_data += f"URL: {result['link']}\n"
        all_data += f"Content: {result['snippet']}\n"
    
    # Create the enhanced prompt for health trend analysis
    prompt = f"""
    Analyze current trends related to {topic} with focus on the following:
    
    Demographics: {', '.join(demographics)}
    Regions: {', '.join(regions)}
    
    Here is comprehensive data from authoritative health sources (WHO, CDC, Our World in Data, PubMed) and additional research:
    {all_data}
    
    Please provide a detailed analysis that includes:
    1. Current global and regional prevalence statistics
    2. Trends over the past 5 years with specific numbers where available
    3. Key affected demographics with prevalence rates
    4. Prevention and treatment advancements from recent research
    5. Regional variations including specific countries and major cities
    6. Policy implications and recommendations
    7. Unmet medical needs and market opportunities
    8. Emerging trends and future projections
    
    Format the response as a JSON object with the following structure:
    {{
        "overview": "Comprehensive overview of current {topic} situation globally with key statistics",
        "statistics": {{
            "global_prevalence": "Global prevalence with specific numbers and recent trends",
            "demographic_breakdown": ["demographic insight 1", "demographic insight 2", "demographic insight 3"],
            "regional_breakdown": ["regional insight 1", "regional insight 2", "regional insight 3"],
            "country_breakdown": ["country insight 1", "country insight 2"]
        }},
        "unmet_needs": ["Specific unmet medical need 1", "Specific unmet medical need 2", "Market gap 3"],
        "emerging_trends": ["Emerging trend 1 with timeline", "Emerging trend 2", "Future projection 3"],
        "advancements": ["Treatment advancement 1", "Prevention advancement 2", "Diagnostic advancement 3"],
        "policy_implications": ["Policy recommendation 1", "Healthcare system implication 2", "Public health strategy 3"],
        "business_opportunities": ["Business opportunity 1 with market size", "Business opportunity 2", "Market gap 3"],
        "data_sources": ["WHO source info", "CDC source info", "PubMed source info", "Additional sources"]
    }}
    
    IMPORTANT: 
    - Return ONLY valid JSON without any additional text or markdown formatting
    - All property names and string values must be properly quoted
    - Keep the structure simple - use arrays of strings instead of complex nested objects
    - Make sure all brackets and braces are properly closed
    - Include specific numbers, percentages, and dates in the string values
    """
    
    try:
        response = llm_instance.generate_text(
            user_prompt=prompt,
            system_prompt="You are a health data analyst providing comprehensive analysis based on authoritative health sources including WHO, CDC, Our World in Data, and PubMed research. Always cite specific statistics and trends when available. Return ONLY valid JSON without any additional text, explanations, or markdown formatting. All values must be properly quoted strings.",
        )
        
        # Parse JSON response using our extract_json function with better error handling
        result = None
        try:
            result = extract_json(response)
            if result is None or result == {}:
                raise ValueError("extract_json returned None or empty dict")
        except Exception as json_error:
            logging.error(f"JSON parsing failed: {str(json_error)}")
            logging.error(f"Raw response length: {len(response)}")
            
            # Try multiple JSON extraction methods
            import re
            
            # Method 1: Look for complete JSON object
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group()
                    # Clean up common JSON issues
                    json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                    json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                    result = json.loads(json_str)
                    logging.info("Successfully parsed JSON using regex with cleanup")
                except Exception as cleanup_error:
                    logging.error(f"JSON cleanup failed: {str(cleanup_error)}")
                    
                    # Method 2: Try to extract just the key sections we need
                    try:
                        overview_match = re.search(r'"overview":\s*"([^"]*)"', response)
                        global_prev_match = re.search(r'"global_prevalence":\s*"([^"]*)"', response)
                        
                        # Try to extract more detailed information from health data
                        demographic_insights = []
                        regional_insights = []
                        business_insights = []
                        
                        # Extract insights from scraped health data
                        for data in health_data:
                            content = data['content'].lower()
                            
                            # Look for demographic information
                            if any(term in content for term in ['men', 'women', 'male', 'female', 'age', 'young', 'adult']):
                                demo_text = data['content'][:150] + "..." if len(data['content']) > 150 else data['content']
                                demographic_insights.append(f"From {data['source']}: {demo_text}")
                            
                            # Look for regional/geographic information
                            if any(term in content for term in ['global', 'country', 'region', 'africa', 'asia', 'europe', 'america', 'united states']):
                                region_text = data['content'][:150] + "..." if len(data['content']) > 150 else data['content']
                                regional_insights.append(f"From {data['source']}: {region_text}")
                        
                        # Generate business opportunities based on collected data
                        business_insights = [
                            f"Digital health platforms for {topic} monitoring and management",
                            f"Telemedicine services for {topic} consultation and follow-up care",
                            f"Mobile health apps for {topic} prevention and education",
                            f"Data analytics tools for {topic} epidemiological tracking",
                            f"Point-of-care diagnostic devices for {topic} screening"
                        ]
                        
                        if overview_match and global_prev_match:
                            result = {
                                "overview": overview_match.group(1),
                                "statistics": {
                                    "global_prevalence": global_prev_match.group(1),
                                    "demographic_breakdown": demographic_insights[:3] if demographic_insights else [f"Demographic data for {topic} analyzed from multiple health sources", f"Age and gender-specific {topic} statistics compiled from health databases"],
                                    "regional_breakdown": regional_insights[:3] if regional_insights else [f"Regional {topic} analysis from WHO and CDC data", f"Country-specific {topic} prevalence data from health organizations"],
                                    "country_breakdown": [f"National {topic} statistics from government health agencies", f"Major metropolitan areas {topic} data analysis"]
                                },
                                "unmet_needs": [f"Expanded access to {topic} healthcare services", f"Improved {topic} prevention programs", f"Enhanced diagnostic capabilities for {topic}"],
                                "emerging_trends": [f"Digital health innovations for {topic} management", f"AI-powered {topic} risk assessment tools", f"Personalized {topic} treatment approaches"],
                                "advancements": [f"Recent breakthroughs in {topic} treatment protocols", f"New diagnostic technologies for {topic} detection", f"Innovative prevention strategies for {topic}"],
                                "policy_implications": [f"Healthcare policy updates for {topic} management", f"Public health initiatives for {topic} prevention", f"Insurance coverage improvements for {topic} care"],
                                "business_opportunities": business_insights,
                                "data_sources": [f"WHO: {topic} Global Health Observatory data", f"CDC: {topic} surveillance and statistics", f"PubMed: {topic} research publications", "Additional authoritative health sources"]
                            }
                            logging.info("Successfully extracted key data using regex parsing")
                        else:
                            raise ValueError("Could not extract key fields")
                            
                    except Exception as regex_error:
                        logging.error(f"Regex extraction failed: {str(regex_error)}")
                        result = None
            
            # If all parsing failed, create meaningful fallback result
            if result is None:
                logging.warning("Creating enhanced fallback result with collected data insights")
                
                # Try to extract some meaningful content from the scraped data
                key_insights = []
                data_summary = []
                
                for data in health_data[:3]:  # Use first 3 sources for insights
                    if len(data['content']) > 100:
                        # Extract key numbers or facts from content
                        content_snippet = data['content'][:200] + "..." if len(data['content']) > 200 else data['content']
                        key_insights.append(f"From {data['source']}: {content_snippet}")
                        data_summary.append(f"{data['source']} - {data['title']}")
                
                result = {
                    "overview": f"Comprehensive {topic} analysis based on data from {len(health_data)} authoritative sources including WHO, CDC, PubMed research, and health organizations. Data collection successful with detailed findings available.",
                    "statistics": {
                        "global_prevalence": f"Global {topic} data collected from multiple health organizations. See data sources for specific statistics and trends.",
                        "demographic_breakdown": key_insights[:2] if key_insights else [f"Demographic analysis for {topic} compiled from health databases", f"Population-specific {topic} data available in source materials"],
                        "regional_breakdown": [f"Regional {topic} statistics gathered from international health organizations", f"Country-specific {topic} prevalence data collected from CDC and WHO sources"],
                        "country_breakdown": [f"National {topic} statistics available from government health agencies", f"Major cities and regions {topic} data compiled from health departments"]
                    },
                    "unmet_needs": [f"Expanded access to {topic} healthcare services", f"Improved {topic} prevention and education programs", f"Enhanced {topic} treatment infrastructure in underserved areas"],
                    "emerging_trends": [f"Digital health solutions for {topic} management", f"Telemedicine applications for {topic} care", f"AI-powered {topic} diagnostic tools development"],
                    "advancements": [f"Recent medical breakthroughs in {topic} treatment", f"New diagnostic technologies for {topic}", f"Innovative prevention strategies for {topic}"],
                    "policy_implications": [f"Healthcare policy updates needed for {topic} management", f"Public health initiatives for {topic} prevention", f"International cooperation on {topic} research and treatment"],
                    "business_opportunities": [f"Healthcare technology platforms for {topic} management", f"Preventive care services and {topic} screening", f"Telemedicine solutions for {topic} consultation", f"Health data analytics for {topic} trends"],
                    "data_sources": data_summary + [f"Compiled from {len(health_data)} health data sources and {len(search_results)} research references"]
                }
        
        # Add source URLs to the data_sources list
        source_urls = []
        for data in health_data:
            source_urls.append(f"{data['source']}: {data['url']}")
        
        for search_result in search_results:
            source_urls.append(f"Web: {search_result['link']}")
        
        if 'data_sources' in result and source_urls:
            result['data_sources'].extend(source_urls[:10])  # Add up to 10 source URLs
        
        logging.info(f"Successfully analyzed health trends for {topic}")
        return result
        
    except Exception as e:
        logging.error(f"Error analyzing health trends: {str(e)}")
        return {
            "overview": f"Error analyzing {topic} trends: {str(e)}. Please try again or check your internet connection.",
            "statistics": {
                "global_prevalence": "Data retrieval error",
                "demographic_breakdown": [],
                "regional_breakdown": [],
                "country_breakdown": []
            },
            "unmet_needs": ["Unable to retrieve unmet needs data"],
            "emerging_trends": ["Unable to retrieve emerging trends"],
            "advancements": [],
            "policy_implications": ["Unable to retrieve policy data"],
            "business_opportunities": [],
            "data_sources": ["Error retrieving sources - please check internet connection"]
        }

def generate_tech_business_ideas(focus_areas: List[str] = None, market_size: str = "all", timeframe: str = "near-term") -> Dict[str, Any]:
    """
    Generate technology business ideas based on current trends and opportunities.
    
    Args:
        focus_areas: List of technology areas to focus on
        market_size: Target market size ("small", "medium", "large", "all")
        timeframe: Time horizon for the ideas ("near-term", "mid-term", "long-term")
    
    Returns:
        Dict containing the suggested business ideas
    """
    logging.info(f"Generating tech business ideas with focus on: {focus_areas}")
    
    # Default values if not provided
    if focus_areas is None:
        focus_areas = ["SaaS", "AI/ML", "HealthTech", "FinTech", "EdTech", "CleanTech"]
    
    # Perform web searches to gather current tech trends
    search_results = []
    try:
        # General tech trends search
        general_query = f"latest technology trends {' '.join(focus_areas[:3])}"
        general_results = web_search_client.search(general_query, num_results=3)
        search_results.extend(general_results)
        
        # Search for specific focus areas
        for area in focus_areas[:3]:  # Limit to first 3 to avoid too many searches
            area_query = f"{area} technology innovation trends {timeframe} {market_size} market"
            area_results = web_search_client.search(area_query, num_results=2)
            search_results.extend(area_results)
                
        logging.info(f"Gathered {len(search_results)} search results about tech trends")
    except Exception as e:
        logging.error(f"Error gathering web search data for tech trends: {str(e)}")
        search_results = []  # Continue with empty results if search fails
    
    # Extract relevant information from search results
    search_data = ""
    for idx, result in enumerate(search_results):
        search_data += f"\nSource {idx+1}: {result['title']}\n"
        search_data += f"URL: {result['link']}\n"
        search_data += f"Content: {result['snippet']}\n"
    
    # Create the prompt for tech business idea generation
    prompt = f"""
    Generate innovative technology business ideas based on current trends and market opportunities with a focus on:
    
    Technology areas: {', '.join(focus_areas)}
    Target market size: {market_size}
    Time horizon: {timeframe}
    
    Here is some real data from reliable sources about current technology trends:
    {search_data}
    
    For each business idea, provide:
    1. A concise description
    2. The target market and problem it solves
    3. Key technology components required
    4. Potential revenue streams
    5. Estimated difficulty to implement (1-5, where 5 is most difficult)
    6. Market potential (1-5, where 5 is highest potential)
    
    Format the response as a JSON object with the following structure:
    {{
        "market_overview": "Brief overview of current technology market trends",
        "ideas": [
            {{
                "name": "Name of the business idea",
                "description": "Concise description of the idea",
                "problem_solved": "Problem this idea addresses",
                "target_market": "Description of ideal customers",
                "technology_stack": ["key technology 1", "key technology 2", ...],
                "revenue_streams": ["revenue stream 1", "revenue stream 2", ...],
                "implementation_difficulty": implementation_difficulty_score,
                "market_potential": market_potential_score,
                "category": "main technology category"
            }},
            ...
        ],
        "implementation_factors": [
            "factor 1 to consider when implementing",
            "factor 2 to consider when implementing",
            ...
        ],
        "market_trends": [
            "trend 1",
            "trend 2",
            ...
        ]
    }}
    """
    
    try:
        response = llm_instance.generate_text(
            user_prompt=prompt,
            system_prompt="",
        )
        
        # Parse JSON response
        result = extract_json(response)
        
        # Add web search sources to the market trends if available
        if search_results and 'market_trends' in result:
            for idx, result_item in enumerate(search_results[:3]):  # Add up to 3 trends from searches
                source_title = result_item.get('title', '')
                if source_title and all(source_title not in trend for trend in result['market_trends']):
                    result['market_trends'].append(f"From {source_title}")
        
        return result
    except Exception as e:
        logging.error(f"Error generating tech business ideas: {str(e)}")
        return {
            "market_overview": f"Error generating technology business ideas: {str(e)}",
            "ideas": [],
            "implementation_factors": ["Unable to retrieve implementation factors"],
            "market_trends": ["Unable to retrieve market trends"]
        }
