import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.utils.document_processor import clean_text, extract_from_html

logger = logging.getLogger(__name__)


class WebsiteCrawler:
    def __init__(self, max_depth: int = 2, max_pages: int = 50):
        self.max_depth = max_depth
        self.max_pages = max_pages

    def _is_same_domain(self, base_url: str, url: str) -> bool:
        return urlparse(base_url).netloc == urlparse(url).netloc

    async def crawl(self, start_url: str) -> list[dict]:
        visited: set[str] = set()
        results: list[dict] = []
        queue: list[tuple[str, int]] = [(start_url, 0)]

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            while queue and len(results) < self.max_pages:
                url, depth = queue.pop(0)
                if url in visited or depth > self.max_depth:
                    continue
                visited.add(url)

                try:
                    response = await client.get(url)
                    if response.status_code != 200:
                        continue
                    content_type = response.headers.get("content-type", "")
                    if "text/html" not in content_type:
                        continue

                    text, _ = extract_from_html(response.content)
                    if len(text) < 100:
                        continue

                    results.append({
                        "url": url,
                        "title": self._extract_title(response.content),
                        "content": text,
                        "depth": depth,
                    })

                    if depth < self.max_depth:
                        links = self._extract_links(response.content, url)
                        for link in links:
                            if link not in visited and self._is_same_domain(start_url, link):
                                queue.append((link, depth + 1))
                except Exception as e:
                    logger.warning("Failed to crawl %s: %s", url, e)

        return results

    def _extract_title(self, content: bytes) -> str:
        soup = BeautifulSoup(content, "lxml")
        title = soup.find("title")
        return clean_text(title.get_text()) if title else "Untitled"

    def _extract_links(self, content: bytes, base_url: str) -> list[str]:
        soup = BeautifulSoup(content, "lxml")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") or href.startswith("mailto:"):
                continue
            full_url = urljoin(base_url, href)
            full_url = full_url.split("#")[0].rstrip("/")
            links.append(full_url)
        return list(set(links))
