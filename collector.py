import requests
import os
from dotenv import load_dotenv

load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

def get_user():
    """
    Fetches the username associated with the github key
    """
    response = requests.get(f'{base_url}/user', headers=headers).json()
    return response.get("login", None)

def get_user_profile(username):
    """
    Fetches basic Github profile information
    """
    response = requests.get(f'{base_url}/users/{username}', headers=headers).json()
    return {
        'login': response.get('login'),
        'public_repos': response.get('public_repos', 0),
        'followers': response.get('followers', 0),
        'following': response.get('following', 0)
    }

def get_all_repos(user):
    """
    Retrieves all public repositories and returns relevant info
    """
    response = requests.get(f'{base_url}/users/{user}/repos', headers=headers).json()
    parsed_repos = []
    for repo in response:
        parsed_repos.append(repo['name'])
    return parsed_repos

def get_stargazers(user, repos):
    """
    Returns total stars and average stars
    """
    total_stars = 0
    num_repos = 0
    for repo in repos:
        response = requests.get(f'{base_url}/repos/{user}/{repo}/stargazers').json()
        num_repos += 1
        if response:
            total_stars += 1
    return (total_stars, float(total_stars/num_repos))

def get_watchers(user, repos):
    """
    Returns total watchers and average watchers
    """
    total_stars = 0
    num_repos = 0
    for repo in repos:
        response = requests.get(f'{base_url}/repos/{user}/{repo}/subscribers').json()
        num_repos += 1
        if response:
            total_stars += 1
    return (total_stars, float(total_stars/num_repos))

def get_repo_commits(owner, repo, per_page=100):
    """
    Gets recent commits from a Github repository
    """
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
    """
    Returns the language distribution in the repository
    """
    response = requests.get(f'{base_url}/repos/{owner}/{repo}/languages', headers=headers).json()
    return response

def get_pull_requests(owner, repo):
    """
    Returns relevant information on pull requests in a repo
    """
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
    """
    Returns the issues on user's public repositories
    """
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


if __name__ == '__main__':
    print(get_watchers("AveryClapp", get_all_repos("AveryClapp")))
