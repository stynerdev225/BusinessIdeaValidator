"""
WHO (World Health Organization) data scraper for health statistics and trends.
"""
import requests
import logging
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import time

class WHOScraper:
    """Scraper for WHO health data and statistics."""
    
    def __init__(self):
        self.base_url = "https://www.who.int"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_health_data(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search WHO for health data on a specific topic.
        
        Args:
            topic: Health topic to search for
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing WHO health data
        """
        results = []
        
        try:
            # WHO search URL
            search_url = f"{self.base_url}/news-room/fact-sheets"
            
            # Try to get WHO fact sheets page
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for fact sheets related to the topic
            fact_sheets = soup.find_all('a', class_='sf-list-vertical__item')
            
            for sheet in fact_sheets[:limit]:
                title = sheet.get_text().strip()
                if topic.lower() in title.lower():
                    link = sheet.get('href', '')
                    if link and not link.startswith('http'):
                        link = self.base_url + link
                    
                    # Try to get the content of the fact sheet
                    content = self._get_fact_sheet_content(link)
                    
                    results.append({
                        'source': 'WHO',
                        'title': title,
                        'url': link,
                        'content': content,
                        'type': 'fact_sheet'
                    })
                    
                    if len(results) >= limit:
                        break
                        
            # If no specific fact sheets found, create general WHO data
            if not results:
                results.append({
                    'source': 'WHO',
                    'title': f'WHO Health Data on {topic}',
                    'url': f"{self.base_url}/news-room/fact-sheets",
                    'content': f"WHO is the directing and coordinating authority on international health within the United Nations system. For {topic} data, WHO provides global health statistics, trend analysis, and policy recommendations.",
                    'type': 'general'
                })
                        
        except Exception as e:
            logging.error(f"Error scraping WHO data for {topic}: {str(e)}")
            # Return fallback data
            results.append({
                'source': 'WHO',
                'title': f'WHO Health Information on {topic}',
                'url': 'https://www.who.int',
                'content': f"WHO provides comprehensive health data and statistics on {topic}. Visit WHO's official website for the latest information.",
                'type': 'fallback'
            })
        
        return results
    
    def _get_fact_sheet_content(self, url: str) -> str:
        """Get content from a WHO fact sheet."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for main content areas
            content_areas = soup.find_all(['div', 'section'], class_=['content', 'main-content', 'article-content'])
            
            content = ""
            for area in content_areas:
                text = area.get_text().strip()
                if len(text) > 100:  # Only include substantial content
                    content += text + " "
            
            # Limit content length
            return content[:1000] + "..." if len(content) > 1000 else content
            
        except Exception as e:
            logging.error(f"Error getting WHO fact sheet content: {str(e)}")
            return "Content unavailable"
        
        finally:
            time.sleep(1)  # Be respectful to WHO servers

def scrape_who_data(topic: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape WHO data for a health topic.
    
    Args:
        topic: Health topic to search for
        limit: Maximum number of results
    
    Returns:
        List of WHO data results
    """
    scraper = WHOScraper()
    return scraper.search_health_data(topic, limit)
