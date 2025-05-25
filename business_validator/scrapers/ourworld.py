"""
Our World in Data scraper for global health statistics and charts.
"""
import requests
import logging
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import time
import json

class OurWorldDataScraper:
    """Scraper for Our World in Data health statistics."""
    
    def __init__(self):
        self.base_url = "https://ourworldindata.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_health_data(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search Our World in Data for health data on a specific topic.
        
        Args:
            topic: Health topic to search for
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing Our World in Data health statistics
        """
        results = []
        
        try:
            # Our World in Data search
            search_url = f"{self.base_url}/search"
            search_params = {'q': topic}
            
            response = self.session.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for search results or charts related to the topic
            chart_links = soup.find_all('a', href=True)
            
            for link in chart_links[:limit*2]:  # Get more to filter
                href = link.get('href', '')
                title = link.get_text().strip()
                
                # Filter for health-related content
                if (topic.lower() in title.lower() or topic.lower() in href.lower()) and len(title) > 10:
                    if not href.startswith('http'):
                        href = self.base_url + href
                    
                    # Get chart/article content
                    content = self._get_chart_content(href)
                    
                    results.append({
                        'source': 'Our World in Data',
                        'title': title,
                        'url': href,
                        'content': content,
                        'type': 'chart_data'
                    })
                    
                    if len(results) >= limit:
                        break
            
            # If no specific results, try direct topic pages
            if not results:
                topic_urls = [
                    f"{self.base_url}/{topic.lower().replace(' ', '-')}",
                    f"{self.base_url}/health",
                    f"{self.base_url}/global-health"
                ]
                
                for url in topic_urls:
                    try:
                        content = self._get_chart_content(url)
                        if content and "unavailable" not in content.lower():
                            results.append({
                                'source': 'Our World in Data',
                                'title': f'Our World in Data: {topic}',
                                'url': url,
                                'content': content,
                                'type': 'topic_page'
                            })
                            break
                    except:
                        continue
                        
            # If still no results, create general data
            if not results:
                results.append({
                    'source': 'Our World in Data',
                    'title': f'Global Data on {topic}',
                    'url': f"{self.base_url}/health",
                    'content': f"Our World in Data provides global statistics and long-term trends for {topic}. The platform offers interactive charts, country comparisons, and historical data to understand global health patterns.",
                    'type': 'general'
                })
                        
        except Exception as e:
            logging.error(f"Error scraping Our World in Data for {topic}: {str(e)}")
            # Return fallback data
            results.append({
                'source': 'Our World in Data',
                'title': f'Global Health Data on {topic}',
                'url': 'https://ourworldindata.org/health',
                'content': f"Our World in Data tracks global health metrics including {topic}. The platform provides data visualizations and analysis of health trends across countries and time periods.",
                'type': 'fallback'
            })
        
        return results
    
    def _get_chart_content(self, url: str) -> str:
        """Get content from an Our World in Data chart or article."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article content and chart descriptions
            content_selectors = [
                '.article-content',
                '.wp-block-column',
                '.chart-subtitle',
                '.chart-description',
                'main article'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if len(text) > 50:
                        content += text + " "
            
            # Look for data insights in script tags (chart data)
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'subtitle' in data:
                        content += f" Chart insight: {data['subtitle']} "
                except:
                    pass
            
            # Clean up the content
            content = ' '.join(content.split())  # Remove extra whitespace
            
            # Limit content length
            return content[:900] + "..." if len(content) > 900 else content
            
        except Exception as e:
            logging.error(f"Error getting Our World in Data content from {url}: {str(e)}")
            return "Content unavailable"
        
        finally:
            time.sleep(1)  # Be respectful to servers

def scrape_ourworld_data(topic: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape Our World in Data for a health topic.
    
    Args:
        topic: Health topic to search for
        limit: Maximum number of results
    
    Returns:
        List of Our World in Data results
    """
    scraper = OurWorldDataScraper()
    return scraper.search_health_data(topic, limit)
