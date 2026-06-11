import os
import time
import schedule
import questionary
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from dotenv import load_dotenv

from agent.storage import StorageManager
from agent.github_client import GitHubClient
from agent.ai_processor import AIProcessor

load_dotenv()
console = Console()
storage = StorageManager()

DEFAULT_INTERESTS = [
    "Artificial Intelligence", "Machine Learning", "Robotics", 
    "Cybersecurity", "Blockchain / Web3", "Game Development",
    "Internet of Things (IoT)", "Quantum Computing", "Data Science",
    "Bioinformatics", "Cloud Native / Kubernetes", "DevOps Tools",
    "Mobile Development (Flutter/React Native)", "Embedded Systems",
    "AR/VR (XR)", "Natural Language Processing (NLP)", "Computer Vision"
]

def run_setup():
    console.print(Panel("[bold cyan]RepoLumin Configuration Wizard[/bold cyan]"))
    console.print("[dim]Tip: Use [bold]SPACE[/bold] to select topics, and [bold]ENTER[/bold] to finish.[/dim]\n")
    
    selected = questionary.checkbox(
        "Which domains would you like to track?",
        choices=DEFAULT_INTERESTS
    ).ask()

    custom = questionary.text("Add any custom keywords (comma separated, or leave blank):").ask()
    if custom:
        selected.extend([k.strip() for k in custom.split(",") if k.strip()])

    if not selected:
        console.print("[red]No interests selected. Please pick at least one topic.[/red]")
        return run_setup()

    mode = questionary.select(
        "Discovery Mode:",
        choices=[
            {"name": "Unique Only (Don't show projects I've already seen)", "value": True},
            {"name": "Scrape All (Show all trending projects, even if seen before)", "value": False}
        ]
    ).ask()

    config = {
        "interests": selected,
        "setup_complete": True,
        "unique_only": mode,
        "last_run": None
    }
    storage.save_config(config)
    console.print("[green]Settings saved successfully![/green]")
    return config

def harvest(target_topics=None):
    console.print(f"\n[bold yellow]--- Initiating Harvest: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---[/bold yellow]")
    
    config = storage.load_config()
    seen_ids = storage.load_seen_repos()
    
    topics_to_run = target_topics if target_topics else config["interests"]
    unique_mode = config.get("unique_only", True)

    github = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    ai = AIProcessor(api_key=os.getenv("GEMINI_API_KEY"))
    
    all_new_projects = []
    
    for topic in topics_to_run:
        console.print(f"[blue]Searching for [bold]{topic}[/bold] projects...[/blue]")
        repos = github.search_repos(topic, max_results=int(os.getenv("MAX_RESULTS_PER_TOPIC", 5)))
        
        harvested_count = 0
        for repo in repos:
            is_unique = repo["id"] not in seen_ids
            
            if not unique_mode or is_unique:
                # Process with AI
                summary = ai.summarize_repo(repo["name"], repo["description"])
                
                project_data = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Topic": topic,
                    "Name": repo["name"],
                    "Summary": summary,
                    "Link": repo["link"],
                    "Stars": repo["stars"]
                }
                all_new_projects.append(project_data)
                if is_unique:
                    seen_ids.add(repo["id"])
                harvested_count += 1
        
        console.print(f"  > Harvested {harvested_count} projects for this topic.")

    if all_new_projects:
        file_path = storage.save_to_spreadsheet(all_new_projects)
        storage.save_seen_repos(seen_ids)
        
        console.print(f"\n[bold green]Success![/bold green] Saved {len(all_new_projects)} projects to:")
        console.print(f"[cyan]{file_path}[/cyan]")
        
        table = Table(title="Harvest Summary")
        table.add_column("Topic", style="magenta")
        table.add_column("Project", style="cyan")
        table.add_column("Stars", justify="right", style="green")
        
        for p in all_new_projects:
            table.add_row(p["Topic"], p["Name"], str(p["Stars"]))
        console.print(table)
    else:
        console.print("[yellow]No projects found in this harvest session.[/yellow]")

def main_menu():
    config = storage.load_config()
    if not config.get("setup_complete"):
        config = run_setup()
        # After first setup, immediately ask for action
    
    while True:
        choice = questionary.select(
            "RepoLumin Control Panel:",
            choices=[
                "Start Background Automation (Daily)",
                "Manual Harvest (Scrape specific topics now)",
                "Full Harvest (Scrape all interests now)",
                "Change Interests / Mode",
                "Exit"
            ]
        ).ask()

        if choice == "Start Background Automation (Daily)":
            harvest() # Run once immediately
            scrape_time = os.getenv("SCRAPE_HOUR_24H", "09:00")
            
            # Clear existing schedules to avoid duplicates
            schedule.clear()
            schedule.every().day.at(scrape_time).do(harvest)
            
            console.print(f"\n[bold green]Background Watcher Active.[/bold green] Scheduled for {scrape_time} daily.")
            console.print("[dim]Press Ctrl+C to return to menu.[/dim]")
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            except KeyboardInterrupt:
                schedule.clear()
                console.print("\n[yellow]Background watcher paused. Returning to menu...[/yellow]")

        elif choice == "Manual Harvest (Scrape specific topics now)":
            topics = questionary.checkbox("Select topics to harvest right now:", choices=config["interests"]).ask()
            if topics:
                harvest(target_topics=topics)
        
        elif choice == "Full Harvest (Scrape all interests now)":
            harvest()

        elif choice == "Change Interests / Mode":
            config = run_setup()

        elif choice == "Exit":
            console.print("[bold red]RepoLumin deactivated.[/bold red]")
            sys.exit()

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Terminated by user.[/bold red]")
        sys.exit()
