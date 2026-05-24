class BrowserPlugin:
    def open_url(self, url: str) -> str:
        return f"URL demandée : {url}"

    def search(self, query: str) -> str:
        return f"Recherche demandée : {query}"
