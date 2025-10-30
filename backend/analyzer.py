import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

class DeveloperAnalyzer:
    def __init__(self, commits, pull_requests, issues, contributors):
        self.commits = commits
        self.pull_requests = pull_requests
        self.issues = issues
        self.contributors = contributors
    
    def analyze_commits(self):
        """Analyze commit patterns"""
        if not self.commits:
            return {}
        
        commit_data = []
        for commit in self.commits:
            try:
                author = commit['commit']['author']['name']
                date = commit['commit']['author']['date']
                commit_data.append({
                    'author': author,
                    'date': datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
                })
            except:
                continue
        
        df = pd.DataFrame(commit_data)
        
        if df.empty:
            return {}
        
        # Calculate metrics
        total_commits = len(df)
        unique_authors = df['author'].nunique()
        commits_per_author = df['author'].value_counts().to_dict()
        
        # Calculate commit frequency (commits per week)
        if len(df) > 1:
            date_range = (df['date'].max() - df['date'].min()).days
            weeks = max(date_range / 7, 1)
            commit_frequency = total_commits / weeks
        else:
            commit_frequency = 0
        
        return {
            'total_commits': total_commits,
            'unique_authors': unique_authors,
            'commits_per_author': commits_per_author,
            'commit_frequency_per_week': round(commit_frequency, 2)
        }
    
    def analyze_pull_requests(self):
        """Analyze pull request metrics"""
        if not self.pull_requests:
            return {}
        
        total_prs = len(self.pull_requests)
        merged_prs = len([pr for pr in self.pull_requests if pr.get('merged_at')])
        open_prs = len([pr for pr in self.pull_requests if pr['state'] == 'open'])
        closed_prs = len([pr for pr in self.pull_requests if pr['state'] == 'closed'])
        
        # Calculate average merge time
        merge_times = []
        for pr in self.pull_requests:
            if pr.get('merged_at') and pr.get('created_at'):
                created = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                merged = datetime.strptime(pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
                merge_times.append((merged - created).total_seconds() / 3600)  # hours
        
        avg_merge_time = round(np.mean(merge_times), 2) if merge_times else 0
        
        return {
            'total_pull_requests': total_prs,
            'merged_prs': merged_prs,
            'open_prs': open_prs,
            'closed_prs': closed_prs,
            'merge_rate': round((merged_prs / total_prs * 100), 2) if total_prs > 0 else 0,
            'avg_merge_time_hours': avg_merge_time
        }
    
    def analyze_issues(self):
        """Analyze issue resolution metrics"""
        # Filter out pull requests from issues
        actual_issues = [issue for issue in self.issues if not issue.get('pull_request')]
        
        if not actual_issues:
            return {}
        
        total_issues = len(actual_issues)
        open_issues = len([i for i in actual_issues if i['state'] == 'open'])
        closed_issues = len([i for i in actual_issues if i['state'] == 'closed'])
        
        # Calculate average resolution time
        resolution_times = []
        for issue in actual_issues:
            if issue.get('closed_at') and issue.get('created_at'):
                created = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                closed = datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
                resolution_times.append((closed - created).total_seconds() / 3600)  # hours
        
        avg_resolution_time = round(np.mean(resolution_times), 2) if resolution_times else 0
        
        return {
            'total_issues': total_issues,
            'open_issues': open_issues,
            'closed_issues': closed_issues,
            'resolution_rate': round((closed_issues / total_issues * 100), 2) if total_issues > 0 else 0,
            'avg_resolution_time_hours': avg_resolution_time
        }
    
    def calculate_efficiency_score(self, commit_metrics, pr_metrics, issue_metrics):
        """Calculate overall developer efficiency score"""
        score = 0
        
        # Commit frequency score (0-30 points)
        commit_freq = commit_metrics.get('commit_frequency_per_week', 0)
        score += min(commit_freq * 2, 30)
        
        # PR merge rate score (0-30 points)
        merge_rate = pr_metrics.get('merge_rate', 0)
        score += merge_rate * 0.3
        
        # Issue resolution rate score (0-30 points)
        resolution_rate = issue_metrics.get('resolution_rate', 0)
        score += resolution_rate * 0.3
        
        # Collaboration score (0-10 points)
        unique_authors = commit_metrics.get('unique_authors', 0)
        score += min(unique_authors * 2, 10)
        
        return round(min(score, 100), 2)
    
    def get_developer_rankings(self, commit_metrics):
        """Rank developers by contribution"""
        commits_per_author = commit_metrics.get('commits_per_author', {})
        
        if not commits_per_author:
            return []
        
        rankings = []
        total_commits = sum(commits_per_author.values())
        
        for author, commits in sorted(commits_per_author.items(), 
                                     key=lambda x: x[1], reverse=True):
            contribution_percentage = round((commits / total_commits * 100), 2)
            rankings.append({
                'developer': author,
                'commits': commits,
                'contribution_percentage': contribution_percentage
            })
        
        return rankings
    
    def generate_report(self):
        """Generate complete analysis report"""
        commit_metrics = self.analyze_commits()
        pr_metrics = self.analyze_pull_requests()
        issue_metrics = self.analyze_issues()
        
        efficiency_score = self.calculate_efficiency_score(
            commit_metrics, pr_metrics, issue_metrics
        )
        
        developer_rankings = self.get_developer_rankings(commit_metrics)
        
        return {
            'efficiency_score': efficiency_score,
            'commit_analysis': commit_metrics,
            'pull_request_analysis': pr_metrics,
            'issue_analysis': issue_metrics,
            'developer_rankings': developer_rankings,
            'summary': {
                'total_contributors': commit_metrics.get('unique_authors', 0),
                'total_commits': commit_metrics.get('total_commits', 0),
                'total_prs': pr_metrics.get('total_pull_requests', 0),
                'total_issues': issue_metrics.get('total_issues', 0)
            }
        }
