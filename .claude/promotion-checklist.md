# Tenkai MCP — Promotion Checklist

## Links
- Site: https://tenkai.blog
- MCP page: https://tenkai.blog/mcp/
- npm: https://www.npmjs.com/package/tenkai-mcp
- Official MCP Registry: https://registry.modelcontextprotocol.io/servers/io.github.mcfredrick/tenkai-mcp
- GitHub: https://github.com/mcfredrick/tenkai

---

## 1. Anthropic MCP Discord

**URL:** https://discord.gg/anthropic (→ #mcp or #show-and-tell channel)

**Message:**
```
Hey! I built tenkai-mcp — a search server for Tenkai Daily (tenkai.blog), an autonomous AI news blog that posts daily summaries of open-source releases, papers, and tools.

Install in one command:
npx tenkai-mcp install

Three tools: search_posts, get_recent_posts, list_tags. No config needed — it fetches a pre-built search index from the live site.

Try asking Claude: "Search tenkai for recent RAG tools" or "What open-source LLM releases came out this week?"

npm: https://www.npmjs.com/package/tenkai-mcp
MCP page: https://tenkai.blog/mcp/
```

**Status:** [ ] Posted

---

## 2. r/LocalLLaMA

**URL:** https://www.reddit.com/r/LocalLLaMA/submit

**Title:**
```
tenkai-mcp: search a daily AI news feed from inside your coding assistant (Claude Code, Cursor, Windsurf)
```

**Body:**
```
I've been running Tenkai Daily (tenkai.blog) — an autonomous blog that posts daily digests of AI open-source releases, papers, and tools. It runs entirely on OpenRouter free-tier models with no human intervention.

I just published an MCP server so you can search it directly from your coding assistant:

**Install:**
npx tenkai-mcp install

(Interactive — detects Claude Code, Claude Desktop, Cursor, Windsurf and patches the right config file)

**Tools:**
- `search_posts` — keyword search across titles, descriptions, tags
- `get_recent_posts` — latest N posts
- `list_tags` — browse by topic

**Example prompts:**
- "Search tenkai for recent RAG tools"
- "What vector database releases came out this week?"
- "Find tenkai posts about fine-tuning"

The search index is pre-built and served as a static JSON from GitHub Pages, so there's no backend to maintain.

npm: https://www.npmjs.com/package/tenkai-mcp
Source: https://github.com/mcfredrick/tenkai
```

**Status:** [ ] Posted

---

## 3. Show HN (Hacker News)

**URL:** https://news.ycombinator.com/submit

**Title:**
```
Show HN: tenkai-mcp – search a daily AI news feed from your coding assistant
```

**Comment (post immediately after submitting):**
```
I run Tenkai Daily (https://tenkai.blog) — an autonomous blog that posts daily digests of open-source AI releases, papers, and dev tools. The pipeline is: OpenRouter free-tier models research the day's news → write a post → Hugo builds → deploys to GitHub Pages. No human in the loop.

I just added an MCP server so you can search the archive from Claude Code, Cursor, Windsurf, etc.:

  npx tenkai-mcp install

It patches your client's config automatically, then you can ask things like "search tenkai for recent RAG tools" or "what came out this week in LLM inference?"

The search index is a static JSON file served from GitHub Pages — no backend, no API keys, no rate limits. The MCP server fetches and caches it on startup.

Tools: search_posts, get_recent_posts, list_tags.

Happy to answer questions about the autonomous publishing pipeline or the MCP side.
```

**Status:** [ ] Posted

---

## 4. Product Hunt

**URL:** https://www.producthunt.com/posts/new

**Name:** `Tenkai MCP`

**Tagline:**
```
Search a daily AI news feed from inside your coding assistant
```

**Description:**
```
Tenkai Daily publishes autonomous daily digests of AI open-source releases, papers, and tools — no human editors, just LLMs and GitHub Actions.

tenkai-mcp is an MCP server that lets you search the full archive from Claude Code, Cursor, Windsurf, or any MCP-compatible coding assistant.

Install with one command: npx tenkai-mcp install

It auto-detects your client and patches the config. Three tools: search by keyword, get recent posts, browse by tag. The search index is a static JSON served from GitHub Pages — no backend, no API keys.

Ask your coding assistant: "What open-source LLM tools came out this week?" and get answers sourced from daily curated posts.
```

**Links:**
- Website: https://tenkai.blog
- GitHub: https://github.com/mcfredrick/tenkai

**Thumbnail/media needed:** Screenshot of Claude Code using the MCP tool in a conversation

**Status:** [ ] Submitted

---

## Registries

| Registry | Status | Notes |
|----------|--------|-------|
| npm | ✅ Done | tenkai-mcp@1.0.2 |
| Official MCP Registry | ✅ Done | io.github.mcfredrick/tenkai-mcp |
| Glama.ai | ⏳ Auto | Crawls GitHub — allow 24h |
| Smithery | ⏸ Skip | Designed for hosted servers, not stdio npm packages |
