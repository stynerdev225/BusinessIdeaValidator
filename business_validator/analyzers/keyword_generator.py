"""
Keyword generation module.
"""
import logging
from typing import List

from SimpleLLM.language.llm import LLM, LLMProvider

# Initialize a single LLM instance for all generators to use
llm_instance = LLM.create(
    provider=LLMProvider.OPENROUTER,
    model_name="deepseek/deepseek-r1",  # Using DeepSeek R1 model
    temperature=0.3,  # Lower temperature for more consistent JSON
    max_tokens=4000   # Increased max_tokens for complete responses
)

def generate_keywords(business_idea: str, num_keywords: int = 3) -> List[str]:
    """
    Generate keywords for searching based on a business idea.
    
    Args:
        business_idea: The business idea to generate keywords for
        num_keywords: Number of keywords to generate
        
    Returns:
        List of generated keywords
    """
    logging.info(f"Generating {num_keywords} keywords for business idea: {business_idea}")
    
    prompt = f"""
    Business Idea: "{business_idea}"
    
    Generate exactly {num_keywords} search keywords or short phrases for researching this business idea.
    The keywords should:
    1. Target potential pain points the idea addresses
    2. Include industry-specific terminology
    3. Be diverse to capture different aspects of the idea
    
    Format: Return ONLY the keywords, one per line, with no numbering or additional text.
    """
    
    try:
        response = llm_instance.generate_text(user_prompt=prompt)
        
        # Process the response
        keywords = [
            keyword.strip() 
            for keyword in response.strip().split("\n") 
            if keyword.strip()
        ]
        
        # Take only the requested number of keywords
        keywords = keywords[:num_keywords]
        
        logging.info(f"Generated {len(keywords)} keywords: {', '.join(keywords)}")
        return keywords
        
    except Exception as e:
        logging.error(f"Error generating keywords: {e}")
        # Fallback to basic keywords based on the idea itself
        words = business_idea.split()
        keywords = [business_idea]
        if len(words) > 2:
            keywords.extend([' '.join(words[:2]), ' '.join(words[-2:])])
        return keywords[:num_keywords]
