"""Source fetchers for the research agent. Each returns raw content or []."""

import os
import re
import sys
from datetime import datetime, timezone, timedelta
from typing import Any

import feedparser
import httpx

from config import BOT_USER_AGENT

HEADERS = {"User-Agent": BOT_USER_AGENT}
TIMEOUT = 20

CLIMATE_KEYWORDS = re.compile(
    r"\b(solar|wind|carbon|climate|energy|battery|grid|renewable|sustainable|"
    r"agriculture|water|biodiversity|ocean|emissions|decarboniz|electr|"
    r"hydrogen|geotherm|biomass|conservation|ecosystem|methane|perovskite|"
    r"microgrid|electrolysis|pyrolysis|heat.pump|fuel.cell)\b",
    re.IGNORECASE,
)


def _get(url: str, **kwargs) -> httpx.Response | None:
    try:
        headers = kwargs.pop("headers", HEADERS)
        r = httpx.get(url, headers=headers, timeout=TIMEOUT, follow_redirects=True, **kwargs)
        r.raise_for_status()
        return r
    except Exception as e:
        print(f"  fetch failed {url}: {e}", file=sys.stderr)
        return None


def _quality_score(repo: dict) -> float:
    now = datetime.now(timezone.utc)
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)

    created_at = datetime.fromisoformat(repo.get("created_at", "1970-01-01T00:00:00Z").replace("Z", "+00:00"))
    pushed_at = datetime.fromisoformat(repo.get("pushed_at", "1970-01-01T00:00:00Z").replace("Z", "+00:00"))
    age_days = max((now - created_at).days, 1)
    pushed_days_ago = (now - pushed_at).days

    score = 0.0

    velocity = stars / age_days
    if velocity >= 10:
        score += 0.30
    elif velocity >= 5:
        score += 0.20
    elif velocity >= 1:
        score += 0.10

    if stars > 0:
        ratio = forks / stars
        if ratio >= 0.15:
            score += 0.20
        elif ratio >= 0.05:
            score += 0.10

    if pushed_days_ago <= 14:
        score += 0.15

    if repo.get("description"):
        score += 0.10

    if repo.get("topics"):
        score += 0.10

    if repo.get("license"):
        score += 0.05

    if stars >= 20:
        score += 0.10

    return min(score, 1.0)


def _rss_feed(url: str, limit: int = 10) -> list[dict]:
    feed = feedparser.parse(url)
    return [
        {"title": e.get("title", ""), "url": e.get("link", ""), "text": e.get("summary", "")}
        for e in feed.entries[:limit]
    ]


def arxiv_climate() -> list[dict]:
    """Fetch recent papers from ArXiv categories relevant to climate engineering."""
    results = []
    for category in ("eess.SY", "physics.ao-ph", "econ.GN", "cond-mat.mtrl-sci"):
        feed = feedparser.parse(f"https://arxiv.org/rss/{category}")
        for entry in feed.entries[:15]:
            results.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "text": entry.get("summary", ""),
            })
    return results


def arxiv_sustainability() -> list[dict]:
    """Fetch recent papers from ArXiv quantitative biology and systems & control."""
    results = []
    for category in ("q-bio.QM", "cs.SY"):
        feed = feedparser.parse(f"https://arxiv.org/rss/{category}")
        for entry in feed.entries[:15]:
            results.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "text": entry.get("summary", ""),
            })
    return results


def github_climate_tools(since_days: int = 30, score_threshold: float = 0.3) -> list[dict]:
    """Search GitHub for climate/energy/sustainability tools and projects."""
    now = datetime.now(timezone.utc)
    since_date = (now - timedelta(days=since_days)).strftime("%Y-%m-%d")

    topics = [
        "solar-energy", "wind-energy", "carbon-footprint", "climate-model",
        "energy-storage", "smart-grid", "renewable-energy", "electric-vehicle",
        "battery", "carbon-accounting", "climate-tech", "energy-transition",
        "direct-air-capture", "carbon-removal", "demand-response", "heat-pump",
    ]

    gh_token = os.environ.get("GH_TOKEN", "")
    gh_headers = {**HEADERS, "Authorization": f"Bearer {gh_token}"} if gh_token else HEADERS

    seen_urls: set[str] = set()
    results = []

    for topic in topics:
        r = _get(
            "https://api.github.com/search/repositories",
            params={
                "q": f"topic:{topic} pushed:>{since_date} stars:>=10",
                "sort": "stars", "order": "desc", "per_page": 10,
            },
            headers=gh_headers,
        )
        if not r:
            continue
        for repo in r.json().get("items", []):
            url = repo.get("html_url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            if _quality_score(repo) < score_threshold:
                continue
            desc = repo.get("description") or ""
            topics_list = " ".join(repo.get("topics", []))
            results.append({
                "title": repo.get("full_name", ""),
                "url": url,
                "text": f"Stars: {repo['stargazers_count']}, Forks: {repo['forks_count']}. {desc}. Topics: {topics_list}",
            })

    return results


def hacker_news_climate() -> list[dict]:
    """Fetch HN stories about climate tech and clean energy."""
    queries = [
        "climate tech", "clean energy", "carbon capture",
        "decarbonization", "net zero", "renewable energy",
        "electric grid", "battery storage",
    ]
    seen: set[str] = set()
    results = []
    for query in queries:
        r = _get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "tags": "story",
                "query": query,
                "numericFilters": "points>10",
                "hitsPerPage": 10,
            },
        )
        if not r:
            continue
        for hit in r.json().get("hits", []):
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            if url in seen:
                continue
            seen.add(url)
            results.append({
                "title": hit.get("title", ""),
                "url": url,
                "text": f"Points: {hit.get('points', 0)}, Comments: {hit.get('num_comments', 0)}",
            })
    return results


def hacker_news_climate_ask() -> list[dict]:
    """Fetch HN Ask HN threads about climate and sustainability."""
    queries = ["climate", "clean energy", "sustainability", "carbon"]
    seen: set[str] = set()
    results = []
    for query in queries:
        r = _get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "tags": "ask_hn",
                "query": query,
                "numericFilters": "points>3",
                "hitsPerPage": 10,
            },
        )
        if not r:
            continue
        for hit in r.json().get("hits", []):
            title = hit.get("title", "")
            if not title or title in seen:
                continue
            seen.add(title)
            results.append({
                "title": title,
                "url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "text": f"Points: {hit.get('points', 0)}, Comments: {hit.get('num_comments', 0)}",
            })
    return results


def github_trending_climate() -> list[dict]:
    """Scrape GitHub trending repos filtered by climate/energy/sustainability keywords."""
    from bs4 import BeautifulSoup

    r = _get("https://github.com/trending?since=daily")
    if not r:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for article in soup.select("article.Box-row"):
        try:
            name_tag = article.select_one("h2 a")
            if not name_tag:
                continue
            repo_path = name_tag["href"].lstrip("/")
            url = f"https://github.com/{repo_path}"
            desc_tag = article.select_one("p")
            desc = desc_tag.get_text(strip=True) if desc_tag else ""
            if not CLIMATE_KEYWORDS.search(repo_path) and not CLIMATE_KEYWORDS.search(desc):
                continue
            results.append({"title": repo_path, "url": url, "text": desc})
        except Exception:
            continue
    return results


def iea_news() -> list[dict]:
    """Fetch IEA news RSS feed."""
    feed = feedparser.parse("https://www.iea.org/feed/news")
    results = []
    for entry in feed.entries[:10]:
        results.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "text": entry.get("summary", ""),
        })
    return results


def nrel_news() -> list[dict]:
    """Fetch NREL news RSS feed."""
    feed = feedparser.parse("https://www.nrel.gov/news/rss.xml")
    results = []
    for entry in feed.entries[:10]:
        results.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "text": entry.get("summary", ""),
        })
    return results


def carbon_brief() -> list[dict]:
    """Fetch Carbon Brief RSS feed."""
    feed = feedparser.parse("https://www.carbonbrief.org/feed/")
    results = []
    for entry in feed.entries[:10]:
        results.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "text": entry.get("summary", ""),
        })
    return results


def cleantechnica() -> list[dict]:
    return _rss_feed("https://cleantechnica.com/feed/")


def canary_media() -> list[dict]:
    return _rss_feed("https://www.canarymedia.com/rss")


def rmi_news() -> list[dict]:
    return _rss_feed("https://rmi.org/feed/")


def arpa_e_news() -> list[dict]:
    return _rss_feed("https://arpa-e.energy.gov/rss.xml")


def doe_news() -> list[dict]:
    return _rss_feed("https://www.energy.gov/rss.xml")


def heatmap_news() -> list[dict]:
    return _rss_feed("https://heatmap.news/feed")


def greentownlabs_jobs() -> list[dict]:
    """Fetch remote job listings from Greentown Labs member companies via Consider API."""
    import httpx as _httpx

    try:
        r = _httpx.post(
            "https://jobs.greentownlabs.com/api-boards/search-jobs",
            json={
                "meta": {"size": 200},
                "board": {"id": "greentown-labs", "isParent": True},
                "query": {},
                "grouped": False,
                "parentSlug": "greentown-labs",
            },
            headers={
                "User-Agent": BOT_USER_AGENT,
                "Accept": "application/json",
                "Referer": "https://jobs.greentownlabs.com/jobs",
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
    except Exception as e:
        print(f"  greentownlabs_jobs fetch failed: {e}", file=sys.stderr)
        return []

    results = []
    seen: set[str] = set()
    for job in r.json().get("jobs", []):
        if not job.get("remote"):
            continue
        url = job.get("applyUrl") or job.get("url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        company = job.get("companyName", "")
        depts = ", ".join(job.get("departments", [])) if job.get("departments") else ""
        text = " — ".join(filter(None, [company, depts, "Remote"]))
        results.append({"title": job.get("title", "").strip(), "url": url, "text": text})

    return results[:15]


ALL_SOURCES: dict[str, Any] = {
    "arxiv_climate": arxiv_climate,
    "arxiv_sustainability": arxiv_sustainability,
    "github_climate_tools": github_climate_tools,
    "github_trending_climate": github_trending_climate,
    "hacker_news_climate": hacker_news_climate,
    "hacker_news_climate_ask": hacker_news_climate_ask,
    "iea_news": iea_news,
    "nrel_news": nrel_news,
    "carbon_brief": carbon_brief,
    "cleantechnica": cleantechnica,
    "canary_media": canary_media,
    "rmi_news": rmi_news,
    "arpa_e_news": arpa_e_news,
    "doe_news": doe_news,
    "heatmap_news": heatmap_news,
    "greentownlabs_jobs": greentownlabs_jobs,
}
