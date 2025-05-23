import requests
import os
from dotenv import load_dotenv
load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

def get_user():
    response = requests.get(f'{base_url}/user', headers=headers).json()
    return response.get("login", None)

def get_user_profile(username):
    response = requests.get(f'{base_url}/users/{username}', headers=headers).json()
    return {
        'login': response.get('login'),
        'public_repos': response.get('public_repos', 0),
        'followers': response.get('followers', 0),
        'following': response.get('following', 0)
    }

def get_all_repos(user):
    response = requests.get(f'{base_url}/users/{user}/repos', headers=headers).json()
    parsed_repos = []
    for repo in response:
        parsed_repos.append({
            'name': repo.get('name'),
            'language': repo.get('language'),
            'stargazers_count': repo.get('stargazers_count', 0),
            'forks_count': repo.get('forks_count', 0),
            'size': repo.get('size', 0),
            'fork': repo.get('fork', False),
            'archived': repo.get('archived', False)
        })
    return parsed_repos

def get_repo_commits(owner, repo, per_page=100):
    commits = []
    page = 1
    while page <= 3:
        response = requests.get(f'{base_url}/repos/{owner}/{repo}/commits', 
                              headers=headers, 
                              params={'per_page': per_page, 'page': page})
        if response.status_code != 200:
            break
        page_commits = response.json()
        if not page_commits:
            break
        
        for commit in page_commits:
            parsed_commit = {
                'message': commit.get('commit', {}).get('message'),
                'additions': commit.get('stats', {}).get('additions', 0) if commit.get('stats') else 0,
                'deletions': commit.get('stats', {}).get('deletions', 0) if commit.get('stats') else 0
            }
            commits.append(parsed_commit)
        page += 1
    return commits

def get_repo_languages(owner, repo):
    response = requests.get(f'{base_url}/repos/{owner}/{repo}/languages', headers=headers).json()
    return response

def get_pull_requests(owner, repo):
    response = requests.get(f'{base_url}/repos/{owner}/{repo}/pulls', 
                          headers=headers, 
                          params={'state': 'all'}).json()
    parsed_prs = []
    for pr in response:
        parsed_prs.append({
            'state': pr.get('state'),
            'additions': pr.get('additions', 0),
            'deletions': pr.get('deletions', 0),
            'changed_files': pr.get('changed_files', 0)
        })
    return parsed_prs

def get_issues(owner, repo):
    response = requests.get(f'{base_url}/repos/{owner}/{repo}/issues', 
                          headers=headers, 
                          params={'state': 'all'}).json()
    parsed_issues = []
    for issue in response:
        if not issue.get('pull_request'):
            parsed_issues.append({
                'state': issue.get('state'),
                'comments': issue.get('comments', 0)
            })
    return parsed_issues

def get_rate_limit():
    response = requests.get(f'{base_url}/rate_limit', headers=headers).json()
    return {
        'remaining': response.get('rate', {}).get('remaining'),
        'reset': response.get('rate', {}).get('reset')
    }

def get_grading_data(username):
    profile = get_user_profile(username)
    repos = get_all_repos(username)
    
    grading_data = {
        'profile': profile,
        'repositories': []
    }
    
    for repo in repos:
        if not repo['fork'] and not repo['archived']:
            repo_data = {
                'details': repo,
                'languages': get_repo_languages(username, repo['name']),
                'commits': get_repo_commits(username, repo['name']),
                'pull_requests': get_pull_requests(username, repo['name']),
                'issues': get_issues(username, repo['name'])
            }
            grading_data['repositories'].append(repo_data)
    
    return grading_data

if __name__ == '__main__':
    data = get_grading_data("AveryClapp")
    print(data)
    print(f"Found {len(data['repositories'])} non-fork repositories")
