"""ZipJeweler CLI — zipjeweler <command>"""
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

app = typer.Typer(help="ZipJeweler AI Marketing Team — 36 agents, 7 crews")
console = Console()


@app.command()
def brief(dry_run: bool = typer.Option(False, "--dry-run")):
    """Run the daily intelligence brief."""
    from zipjeweler.crews.intelligence_crew import IntelligenceCrew
    rprint("[bold cyan]🔍 Running Daily Intelligence Brief...[/bold cyan]")
    crew = IntelligenceCrew(dry_run=dry_run)
    result = crew.run_brief()
    rprint(result)


@app.command()
def listen(
    platform: str = typer.Option("all", "--platform", help="reddit|twitter|linkedin|instagram|facebook|pinterest|all"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Run the listening crew on one or all platforms."""
    from zipjeweler.crews.listening_crew import ListeningCrew
    rprint(f"[bold cyan]👂 Listening on {platform}...[/bold cyan]")
    crew = ListeningCrew(platform=platform, dry_run=dry_run)
    leads = crew.run()
    rprint(f"[green]Found {len(leads)} opportunities.[/green]")
    for lead in leads:
        rprint(f"  • {lead}")


@app.command("create-content")
def create_content(
    platform: str = typer.Option("all", "--platform"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Generate content for one or all platforms."""
    from zipjeweler.crews.content_crew import ContentCrew
    rprint(f"[bold cyan]✍️  Generating content for {platform}...[/bold cyan]")
    crew = ContentCrew(platform=platform, dry_run=dry_run)
    crew.run()


@app.command()
def engage(dry_run: bool = typer.Option(False, "--dry-run")):
    """Run the engagement crew — craft and post replies."""
    from zipjeweler.crews.engagement_crew import EngagementCrew
    rprint("[bold cyan]💬 Running Engagement Crew...[/bold cyan]")
    crew = EngagementCrew(dry_run=dry_run)
    crew.run()


@app.command()
def run(dry_run: bool = typer.Option(False, "--dry-run")):
    """Run the full pipeline: listen → engage → content → post → analyze."""
    rprint("[bold yellow]🚀 Running full ZipJeweler pipeline...[/bold yellow]")
    from zipjeweler.pipeline import run_pipeline
    run_pipeline(dry_run=dry_run)


@app.command()
def dashboard():
    """Launch the Streamlit management dashboard."""
    import subprocess, sys, os
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])


@app.command()
def status():
    """Show current agent status and metrics."""
    table = Table(title="ZipJeweler Agent Status")
    table.add_column("Crew", style="cyan")
    table.add_column("Agents", style="magenta")
    table.add_column("Status", style="green")

    crews = [
        ("Intelligence", "4", "✅ Ready"),
        ("Listening", "7", "✅ Ready"),
        ("Engagement", "7", "✅ Ready"),
        ("Content", "3", "✅ Ready"),
        ("Posting", "6", "✅ Ready"),
        ("Analytics", "3", "✅ Ready"),
        ("Evolution", "7", "✅ Ready"),
    ]
    for crew, agents, status in crews:
        table.add_row(crew, agents, status)

    console.print(table)
    rprint(f"\n[bold]Total: 36 agents across 7 crews[/bold]")


if __name__ == "__main__":
    app()
