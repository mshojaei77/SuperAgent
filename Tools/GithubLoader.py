import os
from dotenv import load_dotenv
import base64
from github import Github
from urllib.parse import urlparse

class GitHubTool:
    def __init__(self, github_token=None):
        self.github_token = github_token
        if self.github_token:
            self.g = Github(self.github_token)
        else:
            self.g = Github()

        # Initialize cache
        self.cache = {}

    def parse_url(self, url):
        # Handle various URL formats
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2:
            return f"{path_parts[-2]}/{path_parts[-1]}"
        else:
            return None

    def load(self, url):
        repo_name = self.parse_url(url)
        if not repo_name:
            return "Invalid URL"

        # Check cache
        if repo_name in self.cache:
            return self.cache[repo_name]

        try:
            repo = self.g.get_repo(repo_name)
        except Exception as e:
            print(f"Error fetching repository: {e}")
            return None
        
        repo_data = {
            "repo_name": repo_name,
            "files": []
        }
        
        try:
            contents = repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    file_data = repo.get_contents(file_content.path)
                    decoded_content = base64.b64decode(file_data.content).decode('utf-8')
                    repo_data["files"].append({
                        "file": file_content.path,
                        "content": decoded_content
                    })
        except Exception as e:
            print(f"Error loading repository contents: {e}")
            return None
        
        # Update cache
        self.cache[repo_name] = repo_data

        return repo_data


if __name__ == "__main__":
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")
    loader = GitHubTool(github_token)
    repo_url = "https://github.com/mshojaei77/Awesome-AI"
    result = loader.load(repo_url)
    print(result)

