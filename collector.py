import requests
import os
from dotenv import load_dotenv

load_dotenv()
github_key = os.getenv("GITHUB_KEY")
# Set your token
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

ENDPOINTS = {
    'user_profile': '/users/{username}',
    'user_repos': '/users/{username}/repos',
    'repo_details': '/repos/{owner}/{repo}',
    'repo_commits': '/repos/{owner}/{repo}/commits',
    'repo_contents': '/repos/{owner}/{repo}/contents/{path}',
    'repo_languages': '/repos/{owner}/{repo}/languages',
    'user_events': '/users/{username}/events',
    'pull_requests': '/repos/{owner}/{repo}/pulls',
    'issues': '/repos/{owner}/{repo}/issues'
}

def get_user():
    response = requests.get(f'{base_url}/user', headers=headers).json()
    return response.get("login", None)

def get_repo_names(user):
    response = requests.get(f'{base_url}/users/{user}/repos').json()
    names = []
    for repo in response:
        names.append(repo["name"])
    return names

def get_repo_details(user, repo):
    response = requests.get(f'{base_url}/repos/{user}/{repo}').json()
    return response
if __name__ == '__main__':
    print(get_repo_names("AveryClapp"))
    print(get_repo_details("AveryClapp", "AveryClapp"))
