"""
Agent Browser - Navigation web, recherche et extraction de données.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests


@dataclass
class WebPage:
    """Représente une page web extraite."""
    url: str
    title: str
    content: str
    links: List[str]
    metadata: Dict[str, Any]


class AgentBrowser:
    """Agent spécialisé pour la navigation web et l'extraction de données."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.history: List[WebPage] = []
        self.current_page: Optional[WebPage] = None
    
    async def navigate(self, url: str) -> WebPage:
        """Navigue vers une URL et extrait le contenu."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraction des informations
            title = soup.title.string if soup.title else "Sans titre"
            
            # Extraction des liens
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    links.append(href)
            
            # Extraction du contenu principal
            content = self._extract_main_content(soup)
            
            # Métadonnées
            metadata = {
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'size': len(response.content)
            }
            
            page = WebPage(
                url=url,
                title=title,
                content=content,
                links=links[:20],  # Limiter à 20 liens
                metadata=metadata
            )
            
            self.current_page = page
            self.history.append(page)
            
            return page
            
        except Exception as e:
            raise Exception(f"Erreur de navigation vers {url}: {str(e)}")
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extrait le contenu principal de la page."""
        # Essayer de trouver le contenu principal
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            return main_content.get_text(strip=True, separator=' ')[:5000]
        
        # Fallback: tout le body
        return soup.body.get_text(strip=True, separator=' ')[:3000] if soup.body else ""
    
    async def search(self, query: str, engine: str = "google") -> List[Dict[str, str]]:
        """Effectue une recherche web et retourne les résultats."""
        if engine.lower() == "google":
            search_url = f"https://www.google.com/search?q={query}"
        elif engine.lower() == "bing":
            search_url = f"https://www.bing.com/search?q={query}"
        else:
            search_url = f"https://www.google.com/search?q={query}"
        
        try:
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            # Extraction des résultats (simplifié)
            for result in soup.find_all('div', class_='g')[:10]:
                title_elem = result.find('h3')
                link_elem = result.find('a')
                snippet_elem = result.find('span', class_='st')
                
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': link_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"Erreur de recherche: {str(e)}")
    
    async def extract_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extrait des données spécifiques de la page courante."""
        if not self.current_page:
            raise Exception("Aucune page chargée")
        
        try:
            response = self.session.get(self.current_page.url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            extracted = {}
            for key, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    extracted[key] = [elem.get_text(strip=True) for elem in elements]
                else:
                    extracted[key] = []
            
            return extracted
            
        except Exception as e:
            raise Exception(f"Erreur d'extraction: {str(e)}")
    
    async def extract_links(self, pattern: Optional[str] = None) -> List[str]:
        """Extrait les liens de la page courante, optionnellement filtrés par pattern."""
        if not self.current_page:
            raise Exception("Aucune page chargée")
        
        links = self.current_page.links
        
        if pattern:
            import re
            links = [link for link in links if re.search(pattern, link)]
        
        return links
    
    async def download_file(self, url: str, destination: str) -> str:
        """Télécharge un fichier depuis une URL."""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return destination
            
        except Exception as e:
            raise Exception(f"Erreur de téléchargement: {str(e)}")
    
    def get_history(self) -> List[WebPage]:
        """Retourne l'historique de navigation."""
        return self.history
    
    def clear_history(self):
        """Efface l'historique de navigation."""
        self.history = []
        self.current_page = None
    
    def close(self):
        """Ferme la session du navigateur."""
        self.session.close()
