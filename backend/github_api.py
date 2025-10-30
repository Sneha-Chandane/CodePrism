import requests
import time
from datetime import datetime
from config import Config

class GitHubAPI:
    def __init__(self):
        self.base_url = Config.GITHUB_API_BASE
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if Config.GITHUB_TOKEN:
            self.headers['Authorization'] = f'token {Config.GITHUB_TOKEN}'
    
    def parse_repo_url(self, repo_url):
        """Extract owner and repo name from GitHub URL"""
        # Handle both https://github.com/owner/repo and owner/repo formats
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            return parts[-2], parts[-1]
        else:
            parts = repo_url.split('/')
            return parts[0], parts[1]
    
    def get_repo_info(self, owner, repo):
        """Get basic repository information"""
        url = f'{self.base_url}/repos/{owner}/{repo}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Failed to fetch repo: {response.status_code}'}
    
    def get_commits(self, owner, repo, per_page=100):
        """Get all commits from repository"""
        commits = []
        page = 1
        
        while True:
            url = f'{self.base_url}/repos/{owner}/{repo}/commits'
            params = {'per_page': per_page, 'page': page}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            if not data:
                break
            
            commits.extend(data)
            page += 1
            
            # Limit to 500 commits for performance
            if len(commits) >= 500:
                break
            
            time.sleep(0.5)  # Rate limiting
        
        return commits
    
    def get_pull_requests(self, owner, repo):
        """Get all pull requests"""
        url = f'{self.base_url}/repos/{owner}/{repo}/pulls'
        params = {'state': 'all', 'per_page': 100}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_issues(self, owner, repo):
        """Get all issues"""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues'
        params = {'state': 'all', 'per_page': 100}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_contributors(self, owner, repo):
        """Get repository contributors"""
        url = f'{self.base_url}/repos/{owner}/{repo}/contributors'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_commit_stats(self, owner, repo):
        """Get commit activity statistics"""
        url = f'{self.base_url}/repos/{owner}/{repo}/stats/commit_activity'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return []
