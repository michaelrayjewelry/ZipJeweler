# ZipJeweler — AI Marketing Team

AI-powered marketing team for [zipjeweler.com](https://zipjeweler.com) — built by Michael Ray Jewelry.

**36 autonomous agents · 7 crews · 5 platforms**

## Platforms

Instagram · Facebook · X/Twitter · Pinterest · TikTok

## Architecture

```
Intelligence Crew → Listening Crew → Engagement Crew → Content Crew → Posting Crew
       ↑                                                                      ↓
       └──────────────── Evolution Crew ← Analytics Crew ←───────────────────┘
                                    ↕
                              FastAPI Backend
                                    ↕
                           Next.js Dashboard
```

## Crews

| Crew | Agents | Purpose |
|------|--------|---------|
| Intelligence | 4 | Daily brief, AI answer monitoring, competitor tracking, opportunity scoring |
| Listening | 7 | Social listening: Instagram, Facebook, X, Pinterest, TikTok |
| Engagement | 7 | Craft and post helpful replies mentioning ZipJeweler |
| Content | 3 | Generate text + image content per platform |
| Posting | 6 | Schedule and publish to all 5 platforms |
| Analytics | 3 | Track engagement, sentiment, learnings |
| Evolution | 7 | A/B testing, strategy evolution, lead nurturing, trend detection |

## Tech Stack

- **Agents:** Python + [CrewAI](https://crewai.com) + Claude API
- **API:** FastAPI
- **Dashboard:** Next.js 14 + Tailwind CSS
- **Data Hub:** Google Sheets

## Quick Start

```bash
# Clone
git clone https://github.com/michaelrayjewelry/ZipJeweler.git
cd ZipJeweler

# Install Python agents
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Fill in your API keys

# Start API
cd api && uvicorn main:app --reload

# Start Dashboard (separate terminal)
cd dashboard && npm install && npm run dev
# → http://localhost:3000

# Run agents (CLI)
zipjeweler status
zipjeweler brief --dry-run
zipjeweler listen --platform instagram --dry-run
zipjeweler run --dry-run
```

## License

MIT
