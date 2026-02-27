"""Full pipeline orchestrator: runs all crews in sequence."""
from rich import print as rprint


def run_pipeline(dry_run: bool = True):
    rprint(f"[bold yellow]Pipeline starting (dry_run={dry_run})...[/bold yellow]")

    steps = [
        ("🔍 Intelligence Brief", "zipjeweler.crews.intelligence_crew", "IntelligenceCrew"),
        ("👂 Listening",          "zipjeweler.crews.listening_crew",    "ListeningCrew"),
        ("💬 Engagement",         "zipjeweler.crews.engagement_crew",   "EngagementCrew"),
        ("✍️  Content",            "zipjeweler.crews.content_crew",      "ContentCrew"),
        ("📤 Posting",            "zipjeweler.crews.posting_crew",      "PostingCrew"),
        ("📊 Analytics",          "zipjeweler.crews.analytics_crew",    "AnalyticsCrew"),
        ("🧬 Evolution",          "zipjeweler.crews.evolution_crew",    "EvolutionCrew"),
    ]

    for label, module_path, class_name in steps:
        rprint(f"\n[cyan]Running {label}...[/cyan]")
        try:
            import importlib
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            crew = cls(dry_run=dry_run)
            crew.run()
            rprint(f"[green]✅ {label} complete[/green]")
        except Exception as e:
            rprint(f"[red]❌ {label} failed: {e}[/red]")

    rprint("\n[bold green]✅ Pipeline complete.[/bold green]")
