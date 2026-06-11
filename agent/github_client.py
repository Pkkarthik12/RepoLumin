import requests
from datetime import datetime, timedelta

class GitHubClient:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com/search/repositories"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        # Only add token if it's provided and not the placeholder
        if token and token != "your_github_token_here":
            self.headers["Authorization"] = f"token {token}"

    def search_repos(self, query, max_results=5):
        """
        Searches for repositories created/updated in the last 24 hours 
        based on the query.
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # GitHub Search Query: search for topic OR keywords created after yesterday
        # This makes it less likely to just match names and more likely to find actual robotics/ros projects
        full_query = f"topic:{query} OR {query} created:>{yesterday}"
        params = {
            "q": full_query,
            "sort": "stars",
            "order": "desc",
            "per_page": max_results
        }

        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            items = response.json().get("items", [])
            
            refined_items = []
            for item in items:
                refined_items.append({
                    "id": item["id"],
                    "name": item["full_name"],
                    "description": item["description"] or "No description provided.",
                    "link": item["html_url"],
                    "stars": item["stargazers_count"]
                })
            return refined_items
        except Exception as e:
            print(f"Error searching GitHub: {e}")
            return []
