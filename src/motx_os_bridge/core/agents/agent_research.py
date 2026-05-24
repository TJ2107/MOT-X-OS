"""
Agent Research - Agent spécialisé pour la recherche et l'analyse.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import re


@dataclass
class ResearchResult:
    """Représente un résultat de recherche."""
    query: str
    sources: List[Dict[str, str]]
    summary: str
    key_insights: List[str]
    confidence: float
    timestamp: str


class AgentResearch:
    """Agent spécialisé pour la recherche et l'analyse."""
    
    def __init__(self):
        self.research_history: List[ResearchResult] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.search_engines = ["google", "bing", "duckduckgo"]
        
        # Import des dépendances
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Vérifie les dépendances disponibles."""
        self.has_requests = self._try_import('requests')
        self.has_bs4 = self._try_import('bs4')
        
        if not self.has_requests:
            print("⚠️ requests non installé - Recherche web limitée")
        if not self.has_bs4:
            print("⚠️ beautifulsoup4 non installé - Parsing HTML limité")
    
    def _try_import(self, module_name: str) -> bool:
        """Tente d'importer un module."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    async def search_web(self, query: str, engine: str = "google", max_results: int = 10) -> List[Dict[str, str]]:
        """Effectue une recherche web."""
        if not self.has_requests:
            raise Exception("requests non installé")
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            if engine == "google":
                url = f"https://www.google.com/search?q={query}"
            elif engine == "bing":
                url = f"https://www.bing.com/search?q={query}"
            else:
                url = f"https://www.google.com/search?q={query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            
            # Parsing des résultats (simplifié)
            if engine == "google":
                for result in soup.find_all('div', class_='g')[:max_results]:
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    snippet_elem = result.find('span', class_='st')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                        })
            else:
                # Parsing générique pour autres moteurs
                for link in soup.find_all('a', href=True)[:max_results]:
                    if link.get('href').startswith('http'):
                        results.append({
                            'title': link.get_text(strip=True),
                            'url': link['href'],
                            'snippet': ''
                        })
            
            return results
            
        except Exception as e:
            raise Exception(f"Erreur recherche web: {str(e)}")
    
    async def deep_research(self, query: str, depth: int = 2) -> ResearchResult:
        """Effectue une recherche approfondie avec analyse."""
        # Recherche initiale
        initial_results = await self.search_web(query, max_results=10)
        
        # Recherche secondaire sur les résultats pertinents
        secondary_results = []
        for result in initial_results[:3]:
            try:
                content = await self._extract_content(result['url'])
                if content:
                    secondary_results.append({
                        'url': result['url'],
                        'content': content[:1000]
                    })
            except:
                continue
        
        # Analyse et synthèse
        summary = await self._synthesize_results(query, initial_results, secondary_results)
        key_insights = await self._extract_insights(summary)
        
        research_result = ResearchResult(
            query=query,
            sources=initial_results,
            summary=summary,
            key_insights=key_insights,
            confidence=0.8,
            timestamp=self._get_timestamp()
        )
        
        self.research_history.append(research_result)
        
        return research_result
    
    async def _extract_content(self, url: str) -> str:
        """Extrait le contenu d'une page web."""
        if not self.has_requests or not self.has_bs4:
            return ""
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraction du contenu principal
            main_content = soup.find('main') or soup.find('article') or soup.body
            if main_content:
                return main_content.get_text(strip=True, separator=' ')[:5000]
            
            return ""
            
        except Exception:
            return ""
    
    async def _synthesize_results(self, query: str, initial_results: List[Dict], secondary_results: List[Dict]) -> str:
        """Synthétise les résultats de recherche."""
        # Synthèse basique (améliorable avec LLM)
        summary_parts = [
            f"Recherche sur: {query}",
            f"{len(initial_results)} sources trouvées"
        ]
        
        if secondary_results:
            summary_parts.append(f"{len(secondary_results)} sources analysées en profondeur")
        
        # Extraction de thèmes communs
        all_text = " ".join([r.get('snippet', '') for r in initial_results])
        all_text += " " + " ".join([r.get('content', '') for r in secondary_results])
        
        # Mots-clés fréquents
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_words:
            keywords = ", ".join([w[0] for w in top_words])
            summary_parts.append(f"Mots-clés: {keywords}")
        
        return " | ".join(summary_parts)
    
    async def _extract_insights(self, summary: str) -> List[str]:
        """Extrait des insights du résumé."""
        insights = []
        
        # Extraction basique d'insights
        if "résultats" in summary.lower():
            insights.append("Plusieurs sources pertinentes identifiées")
        
        if "mots-clés" in summary.lower():
            insights.append("Thèmes récurrents détectés")
        
        if not insights:
            insights.append("Analyse complémentaire recommandée")
        
        return insights
    
    async def analyze_data(self, data: List[Any], analysis_type: str = "general") -> Dict[str, Any]:
        """Analyse des données."""
        analysis = {
            "type": analysis_type,
            "data_points": len(data),
            "timestamp": self._get_timestamp()
        }
        
        if analysis_type == "numeric":
            # Analyse numérique
            numeric_data = [float(d) for d in data if isinstance(d, (int, float))]
            if numeric_data:
                analysis["mean"] = sum(numeric_data) / len(numeric_data)
                analysis["min"] = min(numeric_data)
                analysis["max"] = max(numeric_data)
                analysis["count"] = len(numeric_data)
        
        elif analysis_type == "text":
            # Analyse textuelle
            text_data = [str(d) for d in data if isinstance(d, str)]
            if text_data:
                all_text = " ".join(text_data)
                analysis["total_chars"] = len(all_text)
                analysis["total_words"] = len(all_text.split())
                analysis["avg_length"] = len(all_text) / len(text_data) if text_data else 0
        
        else:
            # Analyse générale
            analysis["data_types"] = list(set(type(d).__name__ for d in data))
        
        return analysis
    
    async def compare_sources(self, sources: List[Dict[str, str]]) -> Dict[str, Any]:
        """Compare plusieurs sources."""
        comparison = {
            "sources_count": len(sources),
            "common_themes": [],
            "differences": [],
            "reliability_score": 0.0
        }
        
        if len(sources) < 2:
            return comparison
        
        # Extraction de mots-clés de chaque source
        all_keywords = []
        for source in sources:
            text = source.get('snippet', '') + " " + source.get('title', '')
            words = re.findall(r'\b\w+\b', text.lower())
            keywords = [w for w in words if len(w) > 3]
            all_keywords.append(set(keywords))
        
        # Thèmes communs
        if all_keywords:
            common = set.intersection(*all_keywords)
            comparison["common_themes"] = list(common)[:10]
        
        # Score de fiabilité (basé sur le nombre de sources)
        comparison["reliability_score"] = min(1.0, len(sources) / 5.0)
        
        return comparison
    
    async def store_knowledge(self, key: str, value: Any):
        """Stocke une connaissance dans la base."""
        self.knowledge_base[key] = {
            "value": value,
            "timestamp": self._get_timestamp()
        }
    
    async def retrieve_knowledge(self, key: str) -> Optional[Any]:
        """Récupère une connaissance de la base."""
        entry = self.knowledge_base.get(key)
        return entry["value"] if entry else None
    
    async def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Recherche dans la base de connaissances."""
        results = []
        query_lower = query.lower()
        
        for key, entry in self.knowledge_base.items():
            if query_lower in key.lower():
                results.append({
                    "key": key,
                    "value": entry["value"],
                    "timestamp": entry["timestamp"]
                })
        
        return results
    
    def get_research_history(self) -> List[ResearchResult]:
        """Retourne l'historique des recherches."""
        return self.research_history
    
    def clear_history(self):
        """Efface l'historique des recherches."""
        self.research_history.clear()
    
    def _get_timestamp(self) -> str:
        """Retourne l'horodatage actuel."""
        from datetime import datetime
        return datetime.now().isoformat()
