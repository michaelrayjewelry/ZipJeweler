"""ZipJeweler Social Media Agents — CLI entry point."""

import click

from zipjeweler.config.settings import get_settings
from zipjeweler.models.database import init_db
from zipjeweler.utils.logger import get_logger, setup_logging


@click.group()
@click.option("--dry-run/--no-dry-run", default=None, help="Override dry run setting")
@click.pass_context
def cli(ctx, dry_run):
    """ZipJeweler Social Media Agents — AI-powered marketing team."""
    setup_logging()
    ctx.ensure_object(dict)

    settings = get_settings()
    if dry_run is not None:
        settings.dry_run = dry_run

    ctx.obj["settings"] = settings
    ctx.obj["logger"] = get_logger("cli")

    # Ensure database tables exist
    init_db()


@cli.command()
@click.pass_context
def brief(ctx):
    """Generate the daily intelligence brief."""
    logger = ctx.obj["logger"]
    settings = ctx.obj["settings"]

    logger.info("Generating daily intelligence brief...")

    from zipjeweler.crews.intelligence_crew import create_intelligence_crew

    crew = create_intelligence_crew()
    result = crew.kickoff()

    logger.info("Daily brief generated", result_length=len(str(result)))
    click.echo("\n" + "=" * 60)
    click.echo("DAILY INTELLIGENCE BRIEF")
    click.echo("=" * 60)
    click.echo(str(result))

    # Sync to Google Sheets
    try:
        from zipjeweler.sheets.intelligence_sheet import sync_intelligence_to_sheet

        sync_intelligence_to_sheet(str(result))
        logger.info("Brief synced to Google Sheets")
    except Exception as e:
        logger.warning("Could not sync to Google Sheets", error=str(e))


@cli.command()
@click.option(
    "--platform",
    type=click.Choice(
        ["reddit", "twitter", "linkedin", "facebook", "instagram", "pinterest", "all"]
    ),
    default="all",
    help="Platform to listen on",
)
@click.pass_context
def listen(ctx, platform):
    """Run social listening agents to discover leads."""
    logger = ctx.obj["logger"]
    settings = ctx.obj["settings"]

    platforms = None if platform == "all" else [platform]
    platform_str = platform if platform != "all" else "all platforms"

    logger.info("Starting social listening", platforms=platform_str, dry_run=settings.dry_run)

    from zipjeweler.crews.listening_crew import create_listening_crew

    crew = create_listening_crew(platforms=platforms)
    result = crew.kickoff()

    logger.info("Listening complete", result_length=len(str(result)))
    click.echo("\n" + "=" * 60)
    click.echo(f"LISTENING RESULTS ({platform_str.upper()})")
    click.echo("=" * 60)
    click.echo(str(result))

    # Sync to Google Sheets
    try:
        from zipjeweler.sheets.listening_sheet import sync_leads_to_sheet

        sync_leads_to_sheet(str(result))
        logger.info("Leads synced to Google Sheets")
    except Exception as e:
        logger.warning("Could not sync to Google Sheets", error=str(e))


@cli.command(name="create-content")
@click.pass_context
def create_content(ctx):
    """Generate content based on discovered leads and intelligence."""
    logger = ctx.obj["logger"]
    logger.info("Content creation not yet implemented (Phase 2)")
    click.echo("Content creation will be available in Phase 2.")


@cli.command()
@click.pass_context
def engage(ctx):
    """Craft replies for discovered leads."""
    logger = ctx.obj["logger"]
    logger.info("Engagement not yet implemented (Phase 2)")
    click.echo("Engagement replies will be available in Phase 2.")


@cli.command()
@click.pass_context
def dashboard(ctx):
    """Launch the Streamlit management dashboard."""
    import subprocess
    import sys
    from pathlib import Path

    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    logger = ctx.obj["logger"]
    logger.info("Launching dashboard", path=str(dashboard_path))

    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(dashboard_path)],
        check=True,
    )


@cli.command()
@click.pass_context
def run(ctx):
    """Run the full pipeline: brief → listen → engage → create → post → analyze."""
    logger = ctx.obj["logger"]
    settings = ctx.obj["settings"]

    logger.info("Running full pipeline", dry_run=settings.dry_run)

    # Phase 1: Intelligence Brief
    click.echo("\n[1/6] Generating daily brief...")
    ctx.invoke(brief)

    # Phase 2: Social Listening
    click.echo("\n[2/6] Running social listening...")
    ctx.invoke(listen, platform="all")

    # Phases 3-6: Not yet implemented
    click.echo("\n[3/6] Engagement — Coming in Phase 2")
    click.echo("[4/6] Content Creation — Coming in Phase 2")
    click.echo("[5/6] Publishing — Coming in Phase 3")
    click.echo("[6/6] Analytics — Coming in Phase 5")

    click.echo("\n" + "=" * 60)
    click.echo("PIPELINE COMPLETE")
    click.echo("=" * 60)


@cli.command(name="init-db")
@click.pass_context
def init_database(ctx):
    """Initialize the database tables."""
    logger = ctx.obj["logger"]
    init_db()
    logger.info("Database initialized successfully")
    click.echo("Database tables created.")


if __name__ == "__main__":
    cli()
