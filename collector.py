import requests
import os
from dotenv import load_dotenv
from github_api import profile_data, popularity_data
from dataclasses import dataclass

load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

@dataclass
class PopularityData:
    stars: int
    avg_stars: float
    watchers: int
    avg_watchers: float
    followers: int
    following: int

@dataclass
class ActivityData:





def collector(): 
    """
    Aggregates all areas of data and sends them via
    gRPC service. Only sends requested ones. (Obviously)
    """
    user, repos = profile_data.get_profile_data()
    pop_data = popularity_data.get_popularity_data(user, repos)
    print(pop_data)
    return 1

      
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
    print(collector())
