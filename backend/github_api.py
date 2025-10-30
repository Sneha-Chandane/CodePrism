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
        self.timeout = 10
    
    def parse_repo_url(self, repo_url):
        """Extract owner and repo name from GitHub URL"""
        try:
            repo_url = repo_url.rstrip('/')
            
            if 'github.com' in repo_url:
                parts = repo_url.split('/')
                for i, part in enumerate(parts):
                    if 'github.com' in part:
                        owner = parts[i + 1]
                        repo = parts[i + 2]
                        return owner, repo
            else:
                parts = repo_url.split('/')
                if len(parts) >= 2:
                    return parts[-2], parts[-1]
            
            raise ValueError("Invalid GitHub URL format")
        except Exception as e:
            raise ValueError(f"Could not parse repository URL: {str(e)}")
    
    def get_repo_info(self, owner, repo):
        """Get basic repository information"""
        url = f'{self.base_url}/repos/{owner}/{repo}'
        
        for attempt in range(3):
            try:
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    return {'error': 'GitHub token invalid or expired'}
                elif response.status_code == 404:
                    return {'error': 'Repository not found'}
                elif response.status_code == 403:
                    return {'error': 'Rate limit exceeded'}
                else:
                    return {'error': f'Failed to fetch repo: {response.status_code}'}
            
            except requests.exceptions.Timeout:
                if attempt < 2:
                    print(f'Timeout, retrying {attempt + 1}/3...')
                    time.sleep(2)
                else:
                    return {'error': 'GitHub API timeout'}
            
            except requests.exceptions.ConnectionError:
                if attempt < 2:
                    print(f'Connection error, retrying {attempt + 1}/3...')
                    time.sleep(2)
                else:
                    return {'error': 'Cannot connect to GitHub'}
            
            except Exception as e:
                return {'error': str(e)}
        
        return {'error': 'Failed after 3 attempts'}
    
    def get_commits(self, owner, repo, per_page=100):
        """Get commits from repository"""
        commits = []
        page = 1
        
        while page <= 5:
            try:
                url = f'{self.base_url}/repos/{owner}/{repo}/commits'
                params = {'per_page': per_page, 'page': page}
                response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                if not data:
                    break
                
                commits.extend(data)
                page += 1
                time.sleep(0.5)
            
            except Exception as e:
                print(f'Error fetching commits: {str(e)}')
                break
        
        return commits
    
    def get_pull_requests(self, owner, repo):
        """Get pull requests"""
        try:
            url = f'{self.base_url}/repos/{owner}/{repo}/pulls'
            params = {'state': 'all', 'per_page': 100}
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f'Error fetching PRs: {str(e)}')
        
        return []
    
    def get_issues(self, owner, repo):
        """Get issues"""
        try:
            url = f'{self.base_url}/repos/{owner}/{repo}/issues'
            params = {'state': 'all', 'per_page': 100}
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f'Error fetching issues: {str(e)}')
        
        return []
    
    def get_contributors(self, owner, repo):
        """Get contributors"""
        try:
            url = f'{self.base_url}/repos/{owner}/{repo}/contributors'
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f'Error fetching contributors: {str(e)}')
        
        return []
