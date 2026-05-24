import webbrowser
import urllib.parse
import urllib.request
from html.parser import HTMLParser


class _HTMLTitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data


class _HTMLLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


class WebPlugin:
    def _normalize_url(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            return "https://" + url
        return url

    def _download_html(self, url: str, timeout: int = 15) -> str:
        url = self._normalize_url(url)
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")

    def _extract_title(self, html: str) -> str:
        parser = _HTMLTitleParser()
        parser.feed(html)
        return parser.title.strip() if parser.title else "Sans titre"

    def _extract_links(self, html: str, max_links: int = 5) -> list[str]:
        parser = _HTMLLinkParser()
        parser.feed(html)
        return parser.links[:max_links]

    def open_url(self, url: str) -> str:
        try:
            url = self._normalize_url(url)
            webbrowser.open(url)
            return f"✅ URL ouverte : {url}"
        except Exception as e:
            return f"❌ Erreur ouverture URL : {e}"

    def search_google(self, query: str) -> str:
        try:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            return f"✅ Recherche Google : {query}"
        except Exception as e:
            return f"❌ Erreur recherche Google : {e}"

    def search_bing(self, query: str) -> str:
        try:
            search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            return f"✅ Recherche Bing : {query}"
        except Exception as e:
            return f"❌ Erreur recherche Bing : {e}"

    def fetch_page(self, url: str) -> str:
        try:
            html = self._download_html(url)
            title = self._extract_title(html)
            links = self._extract_links(html)
            link_summary = ", ".join(links) if links else "(aucun lien trouvé)"
            snippet = html[:1200].replace("\n", " ").strip()
            return (
                f"✅ Page chargée : {url}\n"
                f"Titre : {title}\n"
                f"Liens trouvés : {link_summary}\n"
                f"Extrait : {snippet}"
            )
        except Exception as e:
            return f"❌ Erreur chargement page : {e}"

    def summarize_page(self, url: str) -> str:
        try:
            html = self._download_html(url)
            title = self._extract_title(html)
            links = self._extract_links(html)
            return (
                f"✅ Résumé de la page : {url}\n"
                f"Titre : {title}\n"
                f"Liens : {', '.join(links) if links else 'aucun lien trouvé'}"
            )
        except Exception as e:
            return f"❌ Erreur résumé page : {e}"

    def download_file(self, url: str, destination: str) -> str:
        try:
            url = self._normalize_url(url)
            urllib.request.urlretrieve(url, destination)
            return f"✅ Fichier téléchargé : {destination}"
        except Exception as e:
            return f"❌ Erreur téléchargement : {e}"
