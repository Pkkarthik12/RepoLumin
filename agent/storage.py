import json
import os
import pandas as pd
from datetime import datetime

class StorageManager:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.config_path = os.path.join(base_dir, "config.json")
        self.seen_repos_path = os.path.join(base_dir, "seen_repos.json")
        self.exports_dir = os.path.join(base_dir, "exports")
        
        if not os.path.exists(self.exports_dir):
            os.makedirs(self.exports_dir)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {"interests": [], "setup_complete": False, "unique_only": True}

    def save_config(self, config):
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)

    def load_seen_repos(self):
        if os.path.exists(self.seen_repos_path):
            with open(self.seen_repos_path, "r") as f:
                return set(json.load(f))
        return set()

    def save_seen_repos(self, seen_ids):
        with open(self.seen_repos_path, "w") as f:
            json.dump(list(seen_ids), f)

    def save_to_spreadsheet(self, data):
        """
        data: List of dictionaries with keys [Date, Topic, Name, Description, Link]
        Saves to exports/projects_YYYY-MM-DD.csv
        """
        if not data:
            return None

        df = pd.DataFrame(data)
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_name = f"projects_{date_str}.csv"
        file_path = os.path.join(self.exports_dir, file_name)

        try:
            if os.path.exists(file_path):
                # Append if file exists
                existing_df = pd.read_csv(file_path)
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df.to_csv(file_path, index=False)
            else:
                df.to_csv(file_path, index=False)
            return file_path
        except PermissionError:
            print(f"\n[bold red]Permission Error:[/bold red] Could not save to {file_path}.")
            print("Please close the CSV file if it is open in another program (like Excel) and try again.")
            return None
        except Exception as e:
            print(f"Error saving spreadsheet: {e}")
            return None
