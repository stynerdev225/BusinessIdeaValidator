"""
Utility functions for generating JSON data from LLM responses.
"""
import json
import logging
from pydantic import ValidationError

def generate_basic_pydantic_json_model(
    model_class, 
    llm_instance, 
    prompt, 
    system_prompt="", 
    max_attempts=3
):
    """
    Generate a Pydantic model from LLM output.
    
    Args:
        model_class: The Pydantic model class to instantiate
        llm_instance: The LLM instance to use
        prompt: The user prompt to send to the LLM
        system_prompt: Optional system prompt
        max_attempts: Number of attempts to make
    
    Returns:
        An instance of the Pydantic model
    """
    for attempt in range(max_attempts):
        try:
            # Generate JSON response from LLM
            llm_response = llm_instance.generate_text(
                user_prompt=prompt,
                system_prompt=system_prompt
            )

            # Clean the response to extract only the JSON part
            clean_response = llm_response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()

            # Parse the JSON
            parsed_data = json.loads(clean_response)

            # Create and return the Pydantic model
            return model_class(**parsed_data)

        except (json.JSONDecodeError, ValidationError, Exception) as e:
            logging.warning(f"Attempt {attempt+1} failed: {str(e)}")
            if attempt == max_attempts - 1:
                raise ValueError(f"Failed to generate valid model after {max_attempts} attempts: {str(e)}")
