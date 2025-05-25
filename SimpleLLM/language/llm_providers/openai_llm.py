"""
OpenAI LLM provider module.
"""
import json
import logging
import os
from typing import Generator

import requests
from dotenv import load_dotenv

load_dotenv()

def generate_text(user_prompt: str, system_prompt: str = "", model: str = "gpt-3.5-turbo", 
                 temperature: float = 0.7, top_p: float = 1.0, max_tokens: int = 2000) -> str:
    """
    Generate text using OpenAI API.
    
    Args:
        user_prompt: The user prompt to send to the LLM
        system_prompt: The system prompt to send to the LLM
        model: OpenAI model to use (default: gpt-3.5-turbo)
        temperature: Temperature parameter (default: 0.7)
        top_p: Top-p parameter (default: 1.0)
        max_tokens: Maximum number of tokens to generate (default: 500)
        
    Returns:
        Generated text as a string
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
        
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt} if system_prompt else None,
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens
    }
    
    # Remove None entries
    data["messages"] = [msg for msg in data["messages"] if msg]
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        logging.error(f"Error from OpenAI API: {response.status_code}, {response.text}")
        raise Exception(f"OpenAI API error: {response.status_code}, {response.text}")
        
    response_data = response.json()
    return response_data["choices"][0]["message"]["content"]

def generate_text_stream(user_prompt: str, system_prompt: str = "", model: str = "gpt-3.5-turbo", 
                        temperature: float = 0.7, top_p: float = 1.0, max_tokens: int = 500) -> Generator[str, None, None]:
    """
    Generate streaming text using OpenAI API.
    
    Args:
        user_prompt: The user prompt to send to the LLM
        system_prompt: The system prompt to send to the LLM
        model: OpenAI model to use (default: gpt-3.5-turbo)
        temperature: Temperature parameter (default: 0.7)
        top_p: Top-p parameter (default: 1.0)
        max_tokens: Maximum number of tokens to generate (default: 500)
        
    Yields:
        Generated text chunks
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
        
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt} if system_prompt else None,
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": True
    }
    
    # Remove None entries
    data["messages"] = [msg for msg in data["messages"] if msg]
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data,
        stream=True
    )
    
    if response.status_code != 200:
        logging.error(f"Error from OpenAI API: {response.status_code}, {response.text}")
        raise Exception(f"OpenAI API error: {response.status_code}")
        
    # Process the streaming response
    for line in response.iter_lines():
        if not line:
            continue
            
        if line.startswith(b'data: '):
            line = line[6:]
            
        if line.strip() == b'[DONE]':
            break
            
        try:
            response_data = json.loads(line)
            content = response_data.get('choices', [{}])[0].get('delta', {}).get('content', '')
            if content:
                yield content
        except json.JSONDecodeError:
            logging.warning(f"Failed to decode JSON from line: {line}")
