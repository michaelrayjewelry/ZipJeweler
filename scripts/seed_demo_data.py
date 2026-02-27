"""Seed the database with demo data for dashboard development/testing."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from random import choice, randint, uniform

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zipjeweler.models.database import Base, get_engine, get_session, init_db
from zipjeweler.models.lead import Lead
from zipjeweler.models.content import Content
from zipjeweler.models.engagement import Engagement
from zipjeweler.models.learning import Intelligence, Learning, Retrospective


def seed():
    init_db()
    session = get_session()

    # --- Leads ---
    platforms = ["reddit", "twitter", "linkedin", "facebook", "instagram", "pinterest"]
    topics = [
        "cad_modelers", "jewelry_designers", "custom_jewelry_questions",
        "jewelry_production", "casting_issues", "looking_for_cad",
        "looking_for_designers", "looking_for_manufacturers", "business_management_pain",
    ]
    segments = ["indie_cad_modelers", "etsy_jewelry_sellers", "brick_and_mortar_stores", "custom_jewelers"]
    statuses = ["new", "reply_drafted", "replied", "contacted", "converted"]
    nurture_stages = ["discovery", "first_touch", "follow_up", "soft_pitch", "conversion"]

    snippets = [
        "Struggling with inventory tracking across Etsy and my physical store...",
        "Just finished this CAD model in MatrixGold, but managing files is a nightmare",
        "Anyone know a good jewelry CRM? I'm drowning in customer follow-ups",
        "Casting defects are killing my margins. Need better production tracking",
        "Looking for a custom engagement ring designer — where do I start?",
        "My repair tracking system (sticky notes) isn't cutting it anymore",
        "Need CAD software recommendations for jewelry design",
        "How do other jewelers handle pricing for custom work?",
        "Looking for a manufacturer for small batch jewelry runs",
        "Anyone use jewelry business management software? Recommendations?",
        "3D printed this ring prototype today — production workflow is chaos though",
        "Lost wax casting setup advice? First timer here",
        "My Etsy shop needs better inventory sync with my workshop",
        "Bench jeweler here — how do you all track repair orders?",
        "Running a jewelry store and need help with consignment management",
    ]

    authors = [
        "JewelerMike42", "CADdesigner_pro", "EtsyGems", "BenchJewelerSue",
        "RingMakerDave", "SilverSmithJen", "GoldWorksLLC", "CustomJewelCo",
        "MatrixGoldUser", "JewelryBizOwner", "CastingKing", "DiamondSetter",
        "PearlDesigner", "WaxCarverPro", "JewelryTechGuru",
    ]

    print("Seeding leads...")
    for i in range(30):
        days_ago = randint(0, 14)
        lead = Lead(
            created_at=datetime.utcnow() - timedelta(days=days_ago, hours=randint(0, 23)),
            platform=choice(platforms),
            source_url=f"https://example.com/post/{1000 + i}",
            author=choice(authors),
            content_snippet=choice(snippets),
            topic_category=choice(topics),
            audience_segment=choice(segments),
            lead_score=randint(20, 95),
            dollar_value=round(uniform(100, 10000), 2),
            pain_point_relevance=round(uniform(0.2, 1.0), 2),
            purchase_intent=round(uniform(0.1, 0.9), 2),
            influence_score=round(uniform(0.1, 0.8), 2),
            nurture_stage=choice(nurture_stages),
            status=choice(statuses),
        )
        session.add(lead)

    # --- Content ---
    print("Seeding content...")
    content_types = ["text", "image", "text_image", "reply"]
    content_statuses = ["draft", "approved", "rejected", "posted"]

    drafts = [
        "Tired of losing inventory? ZipJeweler tracks every piece across your store and Etsy shop.",
        "I used to spend 3 hours a week on inventory. Now it takes 10 minutes with ZipJeweler.",
        "Every jeweler I know struggles with inventory. Here's what changed for me.",
        "Great insights on jewelry production challenges. Tools like ZipJeweler are streamlining operations.",
        "Casting defects kill margins. Here's how modern jewelry tools prevent the most common ones.",
        "5 Common Casting Defects and How to Prevent Them — A guide for bench jewelers.",
        "Your repair tracking system shouldn't be sticky notes. There's a better way.",
        "CAD handoff to production doesn't have to be chaos. Here's our workflow.",
    ]

    for i in range(15):
        days_ago = randint(0, 10)
        ct = Content(
            created_at=datetime.utcnow() - timedelta(days=days_ago),
            target_platform=choice(platforms),
            content_type=choice(content_types),
            text_draft=choice(drafts),
            strategy_notes=f"Based on trending {choice(topics)} discussions",
            topic_category=choice(topics),
            ab_variant=choice(["A", "B", "C", ""]),
            ab_test_group=f"test_{randint(1, 5)}" if randint(0, 1) else "",
            status=choice(content_statuses),
        )
        session.add(ct)

    # --- Engagements ---
    print("Seeding engagements...")
    for i in range(20):
        days_ago = randint(0, 14)
        eng = Engagement(
            created_at=datetime.utcnow() - timedelta(days=days_ago),
            content_id=randint(1, 15),
            platform=choice(platforms),
            post_url=f"https://example.com/published/{2000 + i}",
            post_type=choice(["organic", "reply", "comment"]),
            likes=randint(0, 150),
            shares=randint(0, 30),
            comments=randint(0, 20),
            clicks=randint(0, 50),
            impressions=randint(100, 5000),
            engagement_rate=round(uniform(0.5, 8.0), 2),
            positive_responses=randint(0, 10),
            negative_responses=randint(0, 3),
            question_responses=randint(0, 5),
            status="published",
        )
        session.add(eng)

    # --- Intelligence ---
    print("Seeding intelligence...")
    intel_types = ["ai_gap", "competitor_move", "keyword_opportunity", "market_shift"]
    intel_descriptions = [
        "ZipJeweler not appearing in ChatGPT for 'best jewelry management software' query",
        "Jewel360 launched new pricing page targeting independent jewelers",
        "'jewelry repair tracking' keyword has 2,400 monthly searches with low competition",
        "Increase in social mentions of 'jewelry business automation' this week",
        "GemLightbox posted comparison content positioning against traditional inventory tools",
        "'CAD to production workflow' trending in jewelry maker communities",
        "Google AI Overview for 'jeweler CRM' doesn't mention ZipJeweler",
        "RepairShopr announced integration with Shopify for jewelry stores",
    ]

    for i in range(10):
        intel = Intelligence(
            created_at=datetime.utcnow() - timedelta(days=randint(0, 7)),
            date=(datetime.utcnow() - timedelta(days=randint(0, 7))).strftime("%Y-%m-%d"),
            type=choice(intel_types),
            description=choice(intel_descriptions),
            dollar_value=round(uniform(500, 25000), 0),
            priority=randint(1, 5),
            competitor=choice(["Jewel360", "GemLightbox", "RepairShopr", "The Edge", ""]),
            source=choice(["ChatGPT", "Google", "Perplexity", "Social Media", "Web Scrape"]),
            draft_content=choice(drafts) if randint(0, 1) else "",
            status=choice(["new", "acting_on", "captured"]),
        )
        session.add(intel)

    # --- Learnings ---
    print("Seeding learnings...")
    insights = [
        ("content", "Story-based testimonial format outperforms pain-point format on Reddit by 2.8x"),
        ("timing", "Posts at 14:00-17:00 UTC get 40% more engagement on Reddit"),
        ("platform", "Reddit produces 5x more qualified leads per hour than Pinterest"),
        ("audience", "Indie CAD modelers respond best to how-to content"),
        ("topic", "Casting-related content drives highest lead scores (avg 78)"),
        ("reply_style", "Casual empathetic replies convert 2x better than professional ones on Reddit"),
        ("keyword", "'jewelry inventory management' has highest lead qualification rate at 85%"),
        ("content", "Posts with specific dollar amounts get 60% more clicks"),
        ("platform", "LinkedIn produces highest-value leads (avg $8,500 est. value)"),
        ("timing", "Tuesday-Thursday posting window yields 2x more engagement than weekends"),
    ]

    for category, insight in insights:
        learn = Learning(
            created_at=datetime.utcnow() - timedelta(days=randint(0, 30)),
            last_validated=datetime.utcnow() - timedelta(days=randint(0, 10)),
            category=category,
            insight=insight,
            evidence=f"Based on {randint(5, 50)} data points over {randint(1, 4)} weeks",
            confidence=round(uniform(30, 95), 1),
            applied=choice([True, False]),
        )
        session.add(learn)

    # --- Retrospectives ---
    print("Seeding retrospectives...")
    retro = Retrospective(
        created_at=datetime.utcnow() - timedelta(days=7),
        date=(datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
        period="Week of Feb 17, 2026",
        type="weekly",
        top_performing_content="Story-based testimonials about inventory management on Reddit",
        top_performing_platform="reddit",
        top_performing_segment="etsy_jewelry_sellers",
        ab_test_results="Variant B (story-based) beat Variant A (pain-point) by 2.8x on Reddit",
        strategy_changes_made="Shifted Reddit content to story-based format. Increased posting frequency on Reddit by 20%.",
        emerging_trends="Rising interest in CAD-to-production workflow automation. Spike in 'jewelry business automation' searches.",
        goals_vs_actual="Lead target: 20/week, Actual: 28. Engagement target: 5%, Actual: 6.2%. Reply conversion: 8%, Actual: 12%.",
        next_period_goals="Increase LinkedIn activity. Test image-based content on Instagram. Reach 40 leads/week.",
        self_improvement_score=15.0,
    )
    session.add(retro)

    session.commit()
    session.close()
    print("Demo data seeded successfully!")


if __name__ == "__main__":
    seed()
