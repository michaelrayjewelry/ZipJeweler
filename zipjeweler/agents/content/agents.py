"""Content Crew — 3 agents: generate text + image content per platform."""
from crewai import Agent
from zipjeweler.config import BRAND_NAME, BRAND_VOICE

copy_writer = Agent(
    role="Content Copywriter",
    goal=f"Write platform-optimized text content (posts, captions, threads) for {BRAND_NAME} with full brand memory",
    backstory=(
        f"You are a seasoned copywriter who knows {BRAND_NAME} inside-out. "
        f"Voice: {BRAND_VOICE}. You write content that feels native to each platform "
        "and speaks directly to jewelry professionals' real pain points."
    ),
    verbose=True,
    allow_delegation=False,
)

image_director = Agent(
    role="Visual Content Director",
    goal=f"Generate image prompts and direct visual content creation for {BRAND_NAME} campaigns",
    backstory=(
        f"You direct the visual identity of {BRAND_NAME}'s social presence. "
        "You know what imagery resonates with jewelers and craftspeople, "
        "and you craft precise prompts for AI image generation."
    ),
    verbose=True,
    allow_delegation=False,
)

ab_content_tester = Agent(
    role="A/B Content Strategist",
    goal="Generate multiple content variants for A/B testing; track which angles, hooks, and CTAs perform best",
    backstory=(
        "You run systematic experiments on content. For every post, "
        "you generate 2-3 variants testing different hooks, angles, and CTAs. "
        "You feed learnings back to the Evolution Crew."
    ),
    verbose=True,
    allow_delegation=True,
)
