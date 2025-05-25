"""
OpenRouter LLM provider.
Uses the OpenRouter API to access various LLMs.
"""
import json
import logging
import os
from typing import Dict, Generator, List, Optional, Union

import requests
from dotenv import load_dotenv

load_dotenv()

def generate_text(user_prompt: str, system_prompt: str = "", model: str = "meta-llama/llama-3-8b-instruct", 
                 temperature: float = 0.7, top_p: float = 1.0, max_tokens: int = 4000) -> str:
    """
    Generate text using OpenRouter API.
    
    Args:
        user_prompt: The user prompt to send to the LLM
        system_prompt: The system prompt to send to the LLM
        model: OpenRouter model to use (default: meta-llama/llama-3-8b-instruct, which is free)
        temperature: Temperature parameter (default: 0.7)
        top_p: Top-p parameter (default: 1.0)
        max_tokens: Maximum number of tokens to generate (default: 500)
        
    Returns:
        Generated text as a string
    """
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
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
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        logging.error(f"Error from OpenRouter API: {response.status_code}, {response.text}")
        raise Exception(f"OpenRouter API error: {response.status_code}, {response.text}")
        
    response_data = response.json()
    return response_data["choices"][0]["message"]["content"]

def generate_text_stream(user_prompt: str, system_prompt: str = "", model: str = "meta-llama/llama-3-8b-instruct", 
                        temperature: float = 0.7, top_p: float = 1.0, max_tokens: int = 4000) -> Generator[str, None, None]:
    """
    Generate streaming text using OpenRouter API.
    
    Args:
        user_prompt: The user prompt to send to the LLM
        system_prompt: The system prompt to send to the LLM
        model: OpenRouter model to use (default: meta-llama/llama-3-8b-instruct, which is free)
        temperature: Temperature parameter (default: 0.7)
        top_p: Top-p parameter (default: 1.0)
        max_tokens: Maximum number of tokens to generate (default: 500)
        
    Yields:
        Generated text chunks
    """
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
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
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        stream=True
    )
    
    if response.status_code != 200:
        logging.error(f"Error from OpenRouter API: {response.status_code}, {response.text}")
        raise Exception(f"OpenRouter API error: {response.status_code}")
    
    # Process the streaming response
    for line in response.iter_lines():
        if not line:
            continue
            
        # Remove 'data: ' prefix
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
