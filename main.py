import os
import time
import schedule
import questionary
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
    console.print(Panel("[bold cyan]Welcome to RepoLumin Setup[/bold cyan]\nLet's configure your daily discovery interests."))
    
    selected = questionary.checkbox(
        "Which domains would you like to track daily?",
        choices=DEFAULT_INTERESTS
    ).ask()

    custom = questionary.text("Add any custom keywords (comma separated, or leave blank):").ask()
    if custom:
        selected.extend([k.strip() for k in custom.split(",") if k.strip()])

    if not selected:
        console.print("[red]No interests selected. Please pick at least one topic.[/red]")
        return run_setup()

    config = {
        "interests": selected,
        "setup_complete": True,
        "last_run": None
    }
    storage.save_config(config)
    console.print("[green]Setup complete! RepoLumin is now ready.[/green]")
    return config

def harvest():
    console.print(f"\n[bold yellow]--- Initiating Harvest: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---[/bold yellow]")
    
    config = storage.load_config()
    seen_ids = storage.load_seen_repos()
    
    github = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    ai = AIProcessor(api_key=os.getenv("GEMINI_API_KEY"))
    
    all_new_projects = []
    
    for topic in config["interests"]:
        console.print(f"[blue]Searching for new [bold]{topic}[/bold] projects...[/blue]")
        repos = github.search_repos(topic, max_results=int(os.getenv("MAX_RESULTS_PER_TOPIC", 5)))
        
        new_for_topic = 0
        for repo in repos:
            if repo["id"] not in seen_ids:
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
                seen_ids.add(repo["id"])
                new_for_topic += 1
        
        console.print(f"  > Found {new_for_topic} unique repositories.")

    if all_new_projects:
        file_path = storage.save_to_spreadsheet(all_new_projects)
        storage.save_seen_repos(seen_ids)
        
        console.print(f"\n[bold green]Success![/bold green] Saved {len(all_new_projects)} new projects to:")
        console.print(f"[cyan]{file_path}[/cyan]")
        
        # Show a summary table
        table = Table(title="Daily Discoveries")
        table.add_column("Topic", style="magenta")
        table.add_column("Project", style="cyan")
        table.add_column("Stars", justify="right", style="green")
        
        for p in all_new_projects:
            table.add_row(p["Topic"], p["Name"], str(p["Stars"]))
        console.print(table)
    else:
        console.print("[yellow]No unique projects found today. Better luck tomorrow![/yellow]")

    console.print(f"\n[dim]Next harvest scheduled for {os.getenv('SCRAPE_HOUR_24H', '09:00')}[/dim]")

def main():
    config = storage.load_config()
    if not config.get("setup_complete"):
        config = run_setup()
    
    # Run once immediately on start
    harvest()
    
    # Schedule daily
    scrape_time = os.getenv("SCRAPE_HOUR_24H", "09:00")
    schedule.every().day.at(scrape_time).do(harvest)
    
    console.print(f"\n[bold green]RepoLumin is active.[/bold green] Keeping watch for new code...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]RepoLumin deactivated. See you tomorrow![/bold red]")
