"""Tests for research_agent categorization logic."""

import json
from pathlib import Path

import pytest
from research_agent import load_watchlist, recategorize, save_watchlist


def item(title, url, summary, category="release"):
    return {"title": title, "url": url, "summary": summary, "category": category}


# --- URL-based rules (deterministic) ---

@pytest.mark.parametrize("url", [
    "https://arxiv.org/abs/2603.17233",
    "https://arxiv.org/abs/2603.17305",
])
def test_arxiv_urls_become_research(url):
    result = recategorize(item("Some Paper", url, "A research paper."))
    assert result["category"] == "research"


@pytest.mark.parametrize("title,url,summary", [
    (
        "pyodide",
        "https://github.com/pyodide/pyodide",
        "Python distribution for browsers/Node.js via WebAssembly.",
    ),
    (
        "newton",
        "https://github.com/newton-physics/newton",
        "GPU-accelerated physics simulation engine for robotics.",
    ),
    (
        "open-swe",
        "https://github.com/langchain-ai/open-swe",
        "Asynchronous coding agent framework.",
    ),
])
def test_github_urls_become_project(title, url, summary):
    result = recategorize(item(title, url, summary))
    assert result["category"] == "project"


# --- URL rules take priority over LLM-assigned category ---

def test_url_rule_overrides_llm_category():
    # LLM called it a "release" but it's on arxiv — should become "research"
    result = recategorize(item(
        "Some Paper",
        "https://arxiv.org/abs/2603.17233",
        "A research paper.",
        category="release",
    ))
    assert result["category"] == "research"


# --- Other fields are preserved ---

def test_recategorize_preserves_other_fields():
    original = {
        "title": "Draft-and-Prune",
        "url": "https://arxiv.org/abs/2603.17233",
        "summary": "Two-stage auto-formalization pipeline.",
        "category": "release",
        "relevance_score": 8,
    }
    result = recategorize(original)
    assert result["title"] == original["title"]
    assert result["summary"] == original["summary"]
    assert result["relevance_score"] == 8
    assert result["category"] == "research"


def test_load_watchlist_missing_file(tmp_path):
    result = load_watchlist(set(), path=tmp_path / "watchlist.txt")
    assert result == []


def test_load_watchlist_returns_urls(tmp_path):
    wl = tmp_path / "watchlist.txt"
    wl.write_text("https://example.com/a\nhttps://example.com/b\n")
    result = load_watchlist(set(), path=wl)
    assert result == ["https://example.com/a", "https://example.com/b"]


def test_load_watchlist_strips_seen_urls(tmp_path):
    wl = tmp_path / "watchlist.txt"
    wl.write_text("https://example.com/a\nhttps://example.com/b\n")
    result = load_watchlist({"https://example.com/a"}, path=wl)
    assert result == ["https://example.com/b"]
    assert "https://example.com/a" not in wl.read_text()
    assert "https://example.com/b" in wl.read_text()


def test_load_watchlist_preserves_comments_and_blanks(tmp_path):
    wl = tmp_path / "watchlist.txt"
    wl.write_text("# my note\nhttps://example.com/a\n\nhttps://example.com/seen\n")
    result = load_watchlist({"https://example.com/seen"}, path=wl)
    assert result == ["https://example.com/a"]
    text = wl.read_text()
    assert "# my note" in text
    assert "https://example.com/seen" not in text
    assert "\n\n" in text  # blank line preserved


def test_load_watchlist_no_filtering_preserves_content(tmp_path):
    wl = tmp_path / "watchlist.txt"
    original = "# comment\nhttps://example.com/a\n\nhttps://example.com/b\n"
    wl.write_text(original)
    result = load_watchlist(set(), path=wl)
    assert result == ["https://example.com/a", "https://example.com/b"]
    text = wl.read_text()
    assert "# comment" in text
    assert "https://example.com/a" in text
    assert "https://example.com/b" in text
    assert "\n\n" in text  # blank line preserved


def test_load_watchlist_empty_file(tmp_path):
    wl = tmp_path / "watchlist.txt"
    wl.write_text("")
    result = load_watchlist(set(), path=wl)
    assert result == []


def test_save_watchlist_missing_file(tmp_path):
    # No file → no error, nothing created
    save_watchlist({"https://example.com/a"}, path=tmp_path / "watchlist.txt")
    assert not (tmp_path / "watchlist.txt").exists()


def test_save_watchlist_removes_consumed(tmp_path):
    wl = tmp_path / "watchlist.txt"
    wl.write_text("https://example.com/a\nhttps://example.com/b\n")
    save_watchlist({"https://example.com/a"}, path=wl)
    text = wl.read_text()
    assert "https://example.com/a" not in text
    assert "https://example.com/b" in text


def test_save_watchlist_preserves_comments(tmp_path):
    wl = tmp_path / "watchlist.txt"
    wl.write_text("# keep me\nhttps://example.com/a\nhttps://example.com/b\n")
    save_watchlist({"https://example.com/b"}, path=wl)
    text = wl.read_text()
    assert "# keep me" in text
    assert "https://example.com/a" in text
    assert "https://example.com/b" not in text
