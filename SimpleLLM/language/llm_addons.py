"""
LLM addons module with helper functions.
"""
from typing import Type, TypeVar, Dict, Any
import json
import logging
from pydantic import BaseModel, ValidationError

from SimpleLLM.language.llm import LLM

T = TypeVar('T', bound=BaseModel)

def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from a text string.
    
    Args:
        text: Text containing JSON data
        
    Returns:
        Parsed JSON as a dictionary
    """
    if not text or not isinstance(text, str):
        logging.error(f"Invalid input to extract_json: {type(text)}")
        return {}
        
    # Clean the response to extract only the JSON part
    clean_response = text.strip()
    
    # Handle various formats the LLM might return
    if "```json" in clean_response:
        # Extract content between ```json and ```
        start = clean_response.find("```json") + 7
        end = clean_response.find("```", start)
        if end != -1:
            clean_response = clean_response[start:end].strip()
    elif "```" in clean_response:
        # Extract content between ``` and ```
        start = clean_response.find("```") + 3
        end = clean_response.find("```", start)
        if end != -1:
            clean_response = clean_response[start:end].strip()
    
    # Additional JSON extraction - find the first { and last }
    first_brace = clean_response.find('{')
    last_brace = clean_response.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        clean_response = clean_response[first_brace:last_brace+1].strip()
    
    # Fix common JSON formatting issues
    clean_response = clean_response.replace('\n', ' ').replace('\\n', ' ')
    clean_response = clean_response.replace('True', 'true').replace('False', 'false')
    clean_response = clean_response.replace('None', 'null')
    clean_response = clean_response.replace("'", '"')  # Replace single quotes with double quotes
    
    # Remove trailing commas in arrays and objects
    clean_response = clean_response.replace(",]", "]").replace(",}", "}")
    
    try:
        # Parse the JSON
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        # More robust parsing approach for malformed JSON
        try:
            import re
            # Find all key-value pairs and rebuild the JSON
            pattern = r'"([^"]+)"\s*:\s*("[^"]*"|[^,}\s]+)'
            matches = re.findall(pattern, clean_response)
            fixed_json = '{'
            for key, value in matches:
                fixed_json += f'"{key}": {value}, '
            fixed_json = fixed_json.rstrip(', ') + '}'
            
            return json.loads(fixed_json)
        except Exception:
            # If all parsing fails, return empty dict instead of raising an error
            logging.error(f"Failed to parse JSON: {e}")
            return {}

def generate_basic_pydantic_json_model(model_class: Type[T], llm_instance: LLM, prompt: str) -> T:
    """
    Generate a Pydantic model using an LLM.
    
    Args:
        model_class: The Pydantic model class to generate
        llm_instance: LLM instance to use for generation
        prompt: The prompt to send to the LLM
        
    Returns:
        An instance of the Pydantic model
    """
    system_prompt = f"""
    You are a helpful AI that generates structured JSON data.
    The user will provide a prompt, and you should respond with valid JSON that matches this schema:
    
    {model_class.model_json_schema()}
    
    Respond ONLY with the JSON. Do not include any other text, explanations, or markdown formatting.
    """
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Generate JSON response from LLM
            llm_response = llm_instance.generate_text(
                user_prompt=prompt,
                system_prompt=system_prompt
            )
            
            # Clean the response to extract only the JSON part
            clean_response = llm_response.strip()
            
            # Handle various formats the LLM might return
            if "```json" in clean_response:
                # Extract content between ```json and ```
                start = clean_response.find("```json") + 7
                end = clean_response.find("```", start)
                if end != -1:
                    clean_response = clean_response[start:end].strip()
            elif "```" in clean_response:
                # Extract content between ``` and ```
                start = clean_response.find("```") + 3
                end = clean_response.find("```", start)
                if end != -1:
                    clean_response = clean_response[start:end].strip()
            
            # Additional JSON extraction - find the first { and last }
            first_brace = clean_response.find('{')
            last_brace = clean_response.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                clean_response = clean_response[first_brace:last_brace+1].strip()
            
            logging.debug(f"Cleaned JSON response: {clean_response[:100]}...")
            
            # Fix common JSON formatting issues
            clean_response = clean_response.replace('\n', ' ').replace('\\n', ' ')
            clean_response = clean_response.replace('True', 'true').replace('False', 'false')
            clean_response = clean_response.replace('None', 'null')
            
            # Parse the JSON
            parsed_data = json.loads(clean_response)
            
            # Create and return the Pydantic model
            return model_class(**parsed_data)
            
        except (json.JSONDecodeError, ValidationError) as e:
            logging.warning(f"Attempt {attempt+1} failed: {str(e)}")
            # If it's the last attempt, try one more robust parse method
            if attempt == max_attempts - 1:
                try:
                    # Try a more lenient JSON parsing approach
                    import re
                    # Find all key-value pairs and rebuild the JSON
                    pattern = r'"([^"]+)"\s*:\s*("[^"]*"|[^,}\s]+)'
                    matches = re.findall(pattern, clean_response)
                    fixed_json = '{'
                    for key, value in matches:
                        fixed_json += f'"{key}": {value}, '
                    fixed_json = fixed_json.rstrip(', ') + '}'
                    
                    parsed_data = json.loads(fixed_json)
                    return model_class(**parsed_data)
                except Exception as robust_error:
                    logging.error(f"Robust parsing also failed: {robust_error}")
                    raise ValueError(f"Failed to generate valid model after {max_attempts} attempts: {str(e)}")
        except Exception as e:
            logging.warning(f"Unexpected error in attempt {attempt+1}: {str(e)}")
            if attempt == max_attempts - 1:
                raise ValueError(f"Failed to generate valid model after {max_attempts} attempts: {str(e)}")
