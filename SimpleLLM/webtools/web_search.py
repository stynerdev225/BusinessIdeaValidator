"""
Web search module for retrieving real-world data.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

class WebSearchClient:
    """
    Client for performing web searches to retrieve real-world data.
    """
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        if not self.serper_api_key:
            logging.warning("SERPER_API_KEY not found in environment variables")
            self.serper_api_key = None
            
        # Fallback to using SerpAPI if Serper is not available
        self.serpapi_api_key = os.getenv("SERPAPI_API_KEY")
        if not self.serpapi_api_key:
            logging.warning("SERPAPI_API_KEY not found in environment variables")
            self.serpapi_api_key = None
            
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a web search using available search API.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            List of search results with title, link, and snippet
        """
        if self.serper_api_key:
            return self._serper_search(query, num_results)
        elif self.serpapi_api_key:
            return self._serpapi_search(query, num_results)
        else:
            logging.error("No search API keys available")
            return self._mock_search_results(query, num_results)
            
    def _serper_search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a search using Serper.dev API.
        """
        try:
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            data = {
                'q': query,
                'num': num_results
            }
            response = requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                logging.error(f"Serper API error: {response.status_code}")
                return self._mock_search_results(query, num_results)
                
            results = response.json().get('organic', [])
            return [
                {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                }
                for item in results[:num_results]
            ]
        except Exception as e:
            logging.error(f"Error performing Serper search: {str(e)}")
            return self._mock_search_results(query, num_results)
            
    def _serpapi_search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a search using SerpAPI.
        """
        try:
            params = {
                'q': query,
                'api_key': self.serpapi_api_key,
                'num': num_results
            }
            response = requests.get(
                'https://serpapi.com/search',
                params=params
            )
            
            if response.status_code != 200:
                logging.error(f"SerpAPI error: {response.status_code}")
                return self._mock_search_results(query, num_results)
                
            results = response.json().get('organic_results', [])
            return [
                {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                }
                for item in results[:num_results]
            ]
        except Exception as e:
            logging.error(f"Error performing SerpAPI search: {str(e)}")
            return self._mock_search_results(query, num_results)
    
    def _mock_search_results(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Generate mock search results when real search APIs are unavailable.
        This is a fallback method to ensure the application works even without API keys.
        """
        logging.warning(f"Using mock search results for: {query}")
        
        # Create some basic mock results based on the query
        sanitized_query = query.lower().replace(" ", "-")
        return [
            {
                'title': f"Information about {query} - Source {i+1}",
                'link': f"https://example.com/{sanitized_query}-info-{i+1}",
                'snippet': f"This would contain real information about {query} from a reliable source. "
                          f"In a real implementation, this would be actual content from search results."
            }
            for i in range(min(num_results, 5))
        ]
