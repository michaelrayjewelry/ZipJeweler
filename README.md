# ZipJeweler — AI Marketing Team

AI-powered marketing team for ZipJeweler — a jewelry business management tool by Michael Ray Jewelry.

## What This Does

A suite of **36 autonomous agents** organized into **7 crews** that work together to find customers and put ZipJeweler in front of jewelers who need it.

| Crew | Agents | Purpose |
|------|--------|---------|
| Intelligence | 4 | Daily brief, AI answer monitoring, competitor tracking, opportunity scoring |
| Listening | 7 | Social listening across Reddit, X, LinkedIn, Instagram, Facebook, Pinterest |
| Engagement | 7 | Craft and post helpful replies mentioning ZipJeweler on discovered leads |
| Content | 3 | Generate text + image content tailored per platform |
| Posting | 6 | Schedule and publish approved content + replies |
| Analytics | 3 | Track engagement, sentiment analysis, extract learnings |
| Evolution | 7 | A/B testing, strategy evolution, lead nurturing, trend detection |

## Architecture

```
Intelligence Crew → Listening Crew → Engagement Crew → Content Crew → Posting Crew
       ↑                                                                      ↓
       └──────────────── Evolution Crew ← Analytics Crew ←───────────────────┘
```

## Quick Start

```bash
# Clone and install
git clone https://github.com/michaelrayjewelry/ZipJeweler.git
cd ZipJeweler
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run daily brief (dry run)
zipjeweler brief --dry-run

# Listen on Reddit (dry run)
zipjeweler listen --platform reddit --dry-run

# Generate content (dry run)
zipjeweler create-content --dry-run

# Launch dashboard
zipjeweler dashboard

# Check agent status
zipjeweler status

# Run full pipeline (dry run)
zipjeweler run --dry-run
```

## Key Features

- **Social Listening** — Monitors 6 platforms for jewelers discussing CAD, casting, custom jewelry, production, inventory
- **Intelligent Engagement** — Crafts natural, helpful replies with platform-specific tone
- **Content Creation** — Generates text + images with full brand memory and A/B testing
- **Learning & Evolution** — Agents evolve their own strategies based on what works
- **Lead Nurturing** — 6-stage funnel from discovery to conversion
- **Streamlit Dashboard** — Management console with crew-specific controls
- **Hybrid Autonomy** — Human approval initially, increasing autonomy as confidence grows

## Built With

- [CrewAI](https://crewai.com) — Multi-agent orchestration
- [Claude API](https://anthropic.com) — Agent intelligence
- [Streamlit](https://streamlit.io) — Dashboard
- Platform APIs: Reddit (PRAW), Twitter (Tweepy), Instagram, LinkedIn, Facebook, Pinterest

## License

MIT
