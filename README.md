# ZipJeweler — AI Marketing Team

AI-powered marketing team for [zipjeweler.com](https://zipjeweler.com) — built by Michael Ray Jewelry.

**36 autonomous agents · 7 crews · 6 platforms**

## What This Does

A suite of 36 autonomous agents organized into 7 crews that work together to find customers and put ZipJeweler in front of jewelers who need it:

| Crew | Agents | Purpose |
|------|--------|---------|
| **Intelligence** | 4 | Daily brief, AI answer monitoring, competitor tracking, opportunity scoring |
| **Listening** | 7 | Social listening across Reddit, X, LinkedIn, Instagram, Facebook, Pinterest |
| **Engagement** | 7 | Craft and post helpful replies mentioning ZipJeweler on discovered leads |
| **Content** | 3 | Generate text + image content tailored per platform |
| **Posting** | 6 | Schedule and publish approved content + replies |
| **Analytics** | 3 | Track engagement, sentiment analysis, extract learnings |
| **Evolution** | 7 | A/B testing, strategy evolution, lead nurturing, trend detection |

## Platforms

Instagram · Facebook · X/Twitter · Pinterest · TikTok · Reddit · LinkedIn

## Key Features

- **Social Listening**: Monitors 6 platforms for jewelers discussing CAD, casting, custom jewelry, production, inventory, and more
- **Intelligent Engagement**: Crafts natural, helpful replies with platform-specific tone
- **Content Creation**: Generates text + images with full brand memory and A/B testing
- **Learning & Evolution**: Agents evolve their own strategies based on what works — prompts, keywords, timing, and priorities auto-adjust
- **Lead Nurturing**: 6-stage funnel from discovery to conversion with multi-touch sequences
- **Google Sheets Hub**: All data syncs to a cloud spreadsheet with direction columns you can write to
- **Dashboard**: Streamlit management console with 9 pages of crew-specific tools
- **Hybrid Autonomy**: Human approval initially, increasing autonomy as confidence grows

## Architecture

```
Intelligence Crew → Listening Crew → Engagement Crew → Content Crew → Posting Crew
       ↑                                                                      ↓
       └──────────────── Evolution Crew ← Analytics Crew ←───────────────────┘
```

## Tech Stack

- **Agents:** Python + [CrewAI](https://crewai.com) + Claude API
- **Dashboard:** Streamlit + Plotly
- **Data:** SQLAlchemy + SQLite
- **Data Hub:** Google Sheets (bidirectional sync)

## Quick Start

```bash
# Clone and install
git clone https://github.com/michaelrayjewelry/ZipJeweler.git
cd ZipJeweler
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your API keys

# Initialize database
zipjeweler init-db

# Run daily brief
zipjeweler brief

# Listen on Reddit (dry run)
zipjeweler listen --platform reddit --dry-run

# Launch dashboard
zipjeweler dashboard
# → http://localhost:8501

# Run full pipeline (dry run)
zipjeweler run --dry-run
```

## Project Structure

```
src/zipjeweler/
├── config/          # Settings, brand guidelines, target audience
├── models/          # SQLAlchemy models (Lead, Content, Engagement, Learning)
├── crews/           # Intelligence & Listening crews + YAML configs
├── agents/          # Agent definitions and configs
├── tools/           # CrewAI tools (lead scoring, Reddit, etc.)
├── platforms/       # Platform wrappers (Reddit, Twitter, etc.)
├── sheets/          # Google Sheets bidirectional sync
├── dashboard/       # Streamlit dashboard (9 pages)
├── utils/           # Logging, rate limiting, retry
└── main.py          # CLI entry point
```

## License

MIT
