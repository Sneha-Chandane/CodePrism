from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from config import Config
from github_api import GitHubAPI
from analyzer import DeveloperAnalyzer
import mysql.connector

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Simple user database (in production, use MySQL)
users = {
    'admin': {'password': 'admin123', 'name': 'Admin User'},
    'sneha': {'password': 'sneha0306@', 'name': 'Sneha Chandane'}
}

def get_db_connection():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except:
        return None

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username]['password'] == password:
        # Generate JWT token
        token = jwt.encode({
            'username': username,
            'name': users[username]['name'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'name': users[username]['name'],
            'username': username
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/analyze', methods=['POST'])
def analyze_repository():
    """Analyze GitHub repository"""
    try:
        data = request.json
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
        
        # Initialize GitHub API
        github = GitHubAPI()
        
        # Parse repository URL
        try:
            owner, repo = github.parse_repo_url(repo_url)
        except:
            return jsonify({'error': 'Invalid GitHub repository URL'}), 400
        
        # Fetch repository data
        print(f'Fetching data for {owner}/{repo}...')
        
        repo_info = github.get_repo_info(owner, repo)
        if 'error' in repo_info:
            return jsonify(repo_info), 400
        
        commits = github.get_commits(owner, repo)
        pull_requests = github.get_pull_requests(owner, repo)
        issues = github.get_issues(owner, repo)
        contributors = github.get_contributors(owner, repo)
        
        print(f'Fetched: {len(commits)} commits, {len(pull_requests)} PRs, {len(issues)} issues')
        
        # Analyze data
        analyzer = DeveloperAnalyzer(commits, pull_requests, issues, contributors)
        report = analyzer.generate_report()
        
        # Add repository info
        report['repository'] = {
            'name': repo_info.get('name'),
            'full_name': repo_info.get('full_name'),
            'description': repo_info.get('description'),
            'stars': repo_info.get('stargazers_count'),
            'forks': repo_info.get('forks_count'),
            'language': repo_info.get('language'),
            'created_at': repo_info.get('created_at'),
            'updated_at': repo_info.get('updated_at')
        }
        
        return jsonify({
            'success': True,
            'data': report
        })
    
    except Exception as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
